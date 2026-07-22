from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from modules.shared.correlation import get_correlation_id
from modules.shared.event_contract import EVENT_SCHEMA_VERSION, build_event_envelope


ROOT = Path(__file__).resolve().parents[2]
RETENTION_CONFIG = ROOT / "config" / "compliance" / "retention_jobs.json"
SENSITIVE_PAYLOAD_KEYS = {
    "address",
    "biometric",
    "biometrics",
    "card",
    "cpf",
    "ctps",
    "document",
    "document_number",
    "email",
    "lat",
    "latitude",
    "lng",
    "longitude",
    "name",
    "phone",
    "prontuario",
    "raw_text",
    "storage_key",
}


@dataclass(frozen=True)
class RetentionCandidate:
    module: str
    record_id: str
    resource_type: str
    subject_id: str | None
    payload: dict[str, Any]
    legal_hold: list[str]
    requested_action: str | None = None
    legal_review_approved: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RetentionCandidate":
        return cls(
            module=str(raw["module"]),
            record_id=str(raw["record_id"]),
            resource_type=str(raw.get("resource_type") or "resource"),
            subject_id=str(raw["subject_id"]) if raw.get("subject_id") else None,
            payload=dict(raw.get("payload") or {}),
            legal_hold=[str(item) for item in raw.get("legal_hold", [])],
            requested_action=str(raw["requested_action"]) if raw.get("requested_action") else None,
            legal_review_approved=bool(raw.get("legal_review_approved", False)),
        )


@dataclass(frozen=True)
class RetentionDecision:
    module: str
    record_id: str
    resource_type: str
    job_name: str
    action: str
    status: str
    audit_event: str
    evidence: dict[str, Any]
    payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "record_id": self.record_id,
            "resource_type": self.resource_type,
            "job_name": self.job_name,
            "action": self.action,
            "status": self.status,
            "audit_event": self.audit_event,
            "evidence": self.evidence,
            "payload": self.payload,
        }


@dataclass(frozen=True)
class RetentionPostgresSettings:
    postgres_dsn: str
    batch_size: int = 100

    @classmethod
    def from_environment(cls) -> "RetentionPostgresSettings":
        dsn = os.getenv("ALL_IN_ONE_RETENTION_POSTGRES_DSN") or os.getenv("ALL_IN_ONE_POSTGRES_DSN")
        if not dsn:
            raise RuntimeError("ALL_IN_ONE_RETENTION_POSTGRES_DSN nao configurada.")
        return cls(
            postgres_dsn=dsn,
            batch_size=max(1, int(os.getenv("ALL_IN_ONE_RETENTION_BATCH_SIZE", "100"))),
        )


def load_retention_config(path: Path = RETENTION_CONFIG) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def selector_hash(candidate: RetentionCandidate) -> str:
    source = {
        "module": candidate.module,
        "record_id": candidate.record_id,
        "resource_type": candidate.resource_type,
        "subject_id": candidate.subject_id,
    }
    return hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def deletion_receipt_hash(candidate: RetentionCandidate, job_name: str, observed_at: datetime) -> str:
    source = {
        "job_name": job_name,
        "module": candidate.module,
        "record_id": candidate.record_id,
        "selector_hash": selector_hash(candidate),
        "observed_at": observed_at.isoformat(),
    }
    return hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def anonymize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        normalized_key = key.casefold()
        if normalized_key in SENSITIVE_PAYLOAD_KEYS or any(token in normalized_key for token in SENSITIVE_PAYLOAD_KEYS):
            redacted[key] = "[anonymized]"
        elif isinstance(value, dict):
            redacted[key] = anonymize_payload(value)
        elif isinstance(value, list):
            redacted[key] = [anonymize_payload(item) if isinstance(item, dict) else item for item in value]
        else:
            redacted[key] = value
    return redacted


def _base_evidence(
    candidate: RetentionCandidate,
    config: dict[str, Any],
    job_name: str,
    observed_at: datetime,
) -> dict[str, Any]:
    rule = config["module_rules"][candidate.module]
    return {
        "job_run_id": f"{job_name}:{observed_at.strftime('%Y%m%dT%H%M%SZ')}",
        "module": candidate.module,
        "policy_version": config["version"],
        "record_selector_hash": selector_hash(candidate),
        "evidence_domain": rule["evidence_domain"],
        "audit_event_id": f"{candidate.module}:{candidate.record_id}:{job_name}",
    }


def decide_retention(
    candidate: RetentionCandidate,
    job_name: str,
    *,
    dry_run: bool = False,
    observed_at: datetime | None = None,
    config: dict[str, Any] | None = None,
) -> RetentionDecision:
    config = config or load_retention_config()
    observed = observed_at or datetime.now(UTC)
    if candidate.module not in config["module_rules"]:
        raise ValueError(f"Modulo sem regra de retencao: {candidate.module}")
    if job_name not in config["jobs"]:
        raise ValueError(f"Job de retencao desconhecido: {job_name}")

    rule = config["module_rules"][candidate.module]
    evidence = _base_evidence(candidate, config, job_name, observed)
    hold_reasons = sorted(set(candidate.legal_hold).intersection(set(rule["legal_hold"])))
    if hold_reasons:
        evidence.update({"hold_reason": ",".join(hold_reasons), "hold_until": "manual_review"})
        return RetentionDecision(
            module=candidate.module,
            record_id=candidate.record_id,
            resource_type=candidate.resource_type,
            job_name=job_name,
            action="legal_hold",
            status="blocked",
            audit_event="compliance.legal_hold.applied",
            evidence=evidence,
            payload=candidate.payload,
        )

    action = candidate.requested_action or rule["default_action"]
    forbidden = set(config["safety_rules"]["forbidden_without_legal_review"])
    if action in forbidden and not candidate.legal_review_approved:
        evidence.update({"hold_reason": "legal_review_required", "hold_until": "approval"})
        return RetentionDecision(
            module=candidate.module,
            record_id=candidate.record_id,
            resource_type=candidate.resource_type,
            job_name=job_name,
            action=action,
            status="blocked",
            audit_event="compliance.legal_hold.applied",
            evidence=evidence,
            payload=candidate.payload,
        )

    if job_name == "retention_review_daily":
        evidence["candidate_count"] = 1
        return RetentionDecision(
            module=candidate.module,
            record_id=candidate.record_id,
            resource_type=candidate.resource_type,
            job_name=job_name,
            action=action,
            status="dry_run" if dry_run else "reviewed",
            audit_event="compliance.retention.reviewed",
            evidence=evidence,
            payload=candidate.payload,
        )

    if job_name == "anonymization_worker_hourly":
        evidence["anonymization_method"] = "field_redaction"
        return RetentionDecision(
            module=candidate.module,
            record_id=candidate.record_id,
            resource_type=candidate.resource_type,
            job_name=job_name,
            action=action,
            status="dry_run" if dry_run else "applied",
            audit_event="compliance.data.anonymized",
            evidence=evidence,
            payload=candidate.payload if dry_run else anonymize_payload(candidate.payload),
        )

    if job_name == "deletion_worker_daily":
        evidence["deletion_receipt_hash"] = deletion_receipt_hash(candidate, job_name, observed)
        return RetentionDecision(
            module=candidate.module,
            record_id=candidate.record_id,
            resource_type=candidate.resource_type,
            job_name=job_name,
            action=action,
            status="dry_run" if dry_run else "applied",
            audit_event="compliance.data.deleted",
            evidence=evidence,
            payload=candidate.payload if dry_run else {"deleted": True, "deleted_at": observed.isoformat()},
        )

    evidence.update({"hold_reason": "legal_hold_reconciliation", "hold_until": "policy_review"})
    return RetentionDecision(
        module=candidate.module,
        record_id=candidate.record_id,
        resource_type=candidate.resource_type,
        job_name=job_name,
        action="legal_hold_reconciliation",
        status="reviewed",
        audit_event="compliance.legal_hold.applied",
        evidence=evidence,
        payload=candidate.payload,
    )


def process_candidates(
    candidates: Iterable[RetentionCandidate],
    job_name: str,
    *,
    dry_run: bool = False,
    observed_at: datetime | None = None,
    config: dict[str, Any] | None = None,
) -> list[RetentionDecision]:
    config = config or load_retention_config()
    observed = observed_at or datetime.now(UTC)
    return [decide_retention(candidate, job_name, dry_run=dry_run, observed_at=observed, config=config) for candidate in candidates]


def candidate_from_postgres_row(row: dict[str, Any]) -> RetentionCandidate:
    legal_hold = row.get("legal_hold") or []
    if isinstance(legal_hold, str):
        legal_hold = json.loads(legal_hold)
    return RetentionCandidate(
        module=str(row["module"]),
        record_id=str(row["resource_id"]),
        resource_type=str(row["resource_type"]),
        subject_id=str(row["subject_id"]) if row.get("subject_id") else None,
        payload=dict(row.get("payload") or {}),
        legal_hold=[str(item) for item in legal_hold],
        requested_action=str(row["requested_action"]) if row.get("requested_action") else None,
        legal_review_approved=bool(row.get("legal_review_approved", False)),
    )


def decision_event_payload(decision: RetentionDecision, candidate_id: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "module": decision.module,
        "resource_type": decision.resource_type,
        "action": decision.action,
        "decision_status": decision.status,
        "job_name": decision.job_name,
        "evidence": {
            "policy_version": decision.evidence["policy_version"],
            "record_selector_hash": decision.evidence["record_selector_hash"],
            "evidence_domain": decision.evidence["evidence_domain"],
        },
    }


class RetentionPostgresStore:
    """Processa candidatos de retencao registrados no PostgreSQL com auditoria e outbox."""

    def __init__(self, settings: RetentionPostgresSettings) -> None:
        self.settings = settings

    def process_pending(
        self,
        job_name: str,
        *,
        dry_run: bool = False,
        observed_at: datetime | None = None,
        config: dict[str, Any] | None = None,
    ) -> list[RetentionDecision]:
        import psycopg
        from psycopg.rows import dict_row

        config = config or load_retention_config()
        observed = observed_at or datetime.now(UTC)
        decisions: list[RetentionDecision] = []
        with psycopg.connect(self.settings.postgres_dsn, row_factory=dict_row) as connection:
            with connection.transaction():
                rows = connection.execute(
                    """SELECT *
                       FROM compliance.retention_candidates
                       WHERE status IN ('pending', 'failed')
                       ORDER BY created_at, id
                       FOR UPDATE SKIP LOCKED
                       LIMIT %s""",
                    (self.settings.batch_size,),
                ).fetchall()
                for row in rows:
                    decision = decide_retention(
                        candidate_from_postgres_row(row),
                        job_name,
                        dry_run=dry_run,
                        observed_at=observed,
                        config=config,
                    )
                    self._record_decision(connection, row, decision, dry_run)
                    decisions.append(decision)
        return decisions

    def _record_decision(
        self,
        connection: Any,
        row: dict[str, Any],
        decision: RetentionDecision,
        dry_run: bool,
    ) -> None:
        from psycopg.types.json import Jsonb

        decision_row = connection.execute(
            """INSERT INTO compliance.retention_decisions
               (candidate_id, module, resource_type, resource_id, job_name, action,
                decision_status, audit_event, evidence, payload, dry_run, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                row["id"],
                decision.module,
                decision.resource_type,
                decision.record_id,
                decision.job_name,
                decision.action,
                decision.status,
                decision.audit_event,
                Jsonb(decision.evidence),
                Jsonb(decision.payload) if decision.payload is not None else None,
                dry_run,
                row.get("created_by"),
            ),
        ).fetchone()
        next_status = "blocked" if decision.status == "blocked" else "dry_run" if dry_run else "processed"
        connection.execute(
            """UPDATE compliance.retention_candidates
               SET status = %s, locked_at = NOW(), updated_at = NOW(), updated_by = %s
               WHERE id = %s""",
            (next_status, row.get("created_by"), row["id"]),
        )
        connection.execute(
            """INSERT INTO audit.logs
               (user_id, actor_user_id, action, module, resource_type, resource_id,
                after_data, status, metadata, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'recorded', %s, %s)""",
            (
                row.get("subject_id"),
                row.get("created_by"),
                decision.audit_event,
                decision.module,
                decision.resource_type,
                decision.record_id,
                Jsonb(decision.to_dict()),
                Jsonb({"retention_candidate_id": str(row["id"]), "retention_decision_id": str(decision_row["id"])}),
                row.get("created_by"),
            ),
        )
        correlation_id = get_correlation_id()
        actor_user_id = str(row.get("created_by") or row.get("subject_id") or "system")
        event_payload = decision_event_payload(decision, str(row["id"]))
        envelope = build_event_envelope(
            module="compliance",
            routing_key=decision.audit_event,
            actor_user_id=actor_user_id,
            item={
                "id": str(decision_row["id"]),
                "resource_type": "retention_decisions",
                "user_id": str(row["subject_id"]) if row.get("subject_id") else None,
                "entity_id": None,
                "idempotency_key": f"{decision.job_name}:{row['id']}:{decision.action}",
                "payload": event_payload,
            },
            correlation_id=correlation_id,
            causation_id=str(row["id"]),
        )
        connection.execute(
            """INSERT INTO audit.domain_events
               (id, user_id, actor_user_id, routing_key, aggregate_type, aggregate_id,
                correlation_id, schema_version, payload, created_by)
               VALUES (%s, %s, %s, %s, 'retention_decisions', %s, %s, %s, %s, %s)""",
            (
                envelope["event_id"],
                row.get("subject_id"),
                row.get("created_by"),
                decision.audit_event,
                decision_row["id"],
                correlation_id,
                EVENT_SCHEMA_VERSION,
                Jsonb(envelope),
                row.get("created_by"),
            ),
        )


def _load_jsonl(path: Path) -> list[RetentionCandidate]:
    candidates: list[RetentionCandidate] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            candidates.append(RetentionCandidate.from_dict(json.loads(line)))
    return candidates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Processa candidatos de retencao LGPD em JSONL.")
    parser.add_argument("--job", required=True, choices=sorted(load_retention_config()["jobs"]))
    parser.add_argument("--input", type=Path, help="Arquivo JSONL com candidatos de retencao.")
    parser.add_argument("--postgres", action="store_true", help="Processa candidatos pendentes em compliance.retention_candidates.")
    parser.add_argument("--postgres-dsn", help="DSN PostgreSQL; se omitido usa ALL_IN_ONE_RETENTION_POSTGRES_DSN.")
    parser.add_argument("--batch-size", type=int, help="Limite de candidatos PostgreSQL por lote.")
    parser.add_argument("--dry-run", action="store_true", help="Calcula decisoes sem aplicar transformacoes destrutivas.")
    args = parser.parse_args(argv)

    if args.postgres:
        settings = (
            RetentionPostgresSettings(args.postgres_dsn, max(1, args.batch_size or 100))
            if args.postgres_dsn
            else RetentionPostgresSettings.from_environment()
        )
        if args.batch_size and not args.postgres_dsn:
            settings = RetentionPostgresSettings(settings.postgres_dsn, max(1, args.batch_size))
        decisions = RetentionPostgresStore(settings).process_pending(args.job, dry_run=args.dry_run)
    else:
        if not args.input:
            parser.error("--input e obrigatorio quando --postgres nao for usado.")
        decisions = process_candidates(_load_jsonl(args.input), args.job, dry_run=args.dry_run)
    for decision in decisions:
        print(json.dumps(decision.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
