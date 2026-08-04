from __future__ import annotations

import hashlib
import hmac
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "config" / "integrations" / "provider_matrix.json"
MONEY = Decimal("0.0001")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _stable_id(prefix: str, *parts: object) -> str:
    material = "|".join(str(part) for part in parts)
    return f"{prefix}_{uuid5(NAMESPACE_URL, material)}"


def _digest(*parts: object) -> str:
    material = "|".join(str(part) for part in parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _money(value: Decimal | str | int | float) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


def _event(routing_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": _stable_id("evt", routing_key, json.dumps(payload, sort_keys=True)),
        "routing_key": routing_key,
        "payload": payload,
        "created_at": _now(),
    }


def sandbox_audit_record(
    provider_key: str,
    adapter: str,
    status: str,
    reference_id: str,
    payload: dict[str, Any],
    events: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    payload_sha256 = _digest(
        "sandbox-payload", json.dumps(payload, sort_keys=True, default=str)
    )
    event_keys = [str(event.get("routing_key", "")) for event in events]
    return {
        "audit_id": _stable_id(
            "sandbox_audit", provider_key, adapter, reference_id, payload_sha256
        ),
        "provider_key": provider_key,
        "adapter": adapter,
        "provider_environment": "sandbox",
        "status": status,
        "reference_id": reference_id,
        "payload_sha256": payload_sha256,
        "event_routing_keys": event_keys,
        "event_count": len(events),
        "retention_policy": "sandbox_audit_90d_no_raw_sensitive_input",
        "created_at": _now(),
    }


def load_provider_matrix(path: Path = MATRIX_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def matrix_by_key(path: Path = MATRIX_PATH) -> dict[str, dict[str, Any]]:
    matrix = load_provider_matrix(path)
    return {item["key"]: item for item in matrix["integrations"]}


@dataclass(frozen=True)
class SandboxResult:
    provider_key: str
    adapter: str
    status: str
    reference_id: str
    payload: dict[str, Any]
    events: tuple[dict[str, Any], ...] = ()

    def audit_record(self) -> dict[str, Any]:
        return sandbox_audit_record(
            self.provider_key,
            self.adapter,
            self.status,
            self.reference_id,
            self.payload,
            self.events,
        )

    def to_response(self) -> dict[str, Any]:
        return {
            "provider_key": self.provider_key,
            "adapter": self.adapter,
            "status": self.status,
            "reference_id": self.reference_id,
            "payload": self.payload,
            "events": list(self.events),
            "audit": self.audit_record(),
        }


class IdentityVerificationSandbox:
    provider_key = "identity_kyc_kyb"
    adapter = "local_identity_verification_simulator"

    def verify_person(
        self,
        user_id: str,
        document: str,
        full_name: str,
        selfie_hash: str | None = None,
        liveness_score: float | None = None,
    ) -> SandboxResult:
        status = (
            "approved"
            if document and full_name and not document.endswith("0000")
            else "manual_review"
        )
        score = 0.97 if status == "approved" else 0.61
        liveness = liveness_score if liveness_score is not None else (0.99 if selfie_hash else 0.74)
        payload = {
            "user_id": user_id,
            "document_hash": _digest("document", document),
            "full_name_hash": _digest("name", full_name.casefold()),
            "selfie_hash": selfie_hash,
            "verification_score": str(score),
            "liveness_score": str(liveness),
            "provider_environment": "sandbox",
            "manual_review_required": status != "approved",
        }
        events = (
            (_event("identity.user.verified", {"user_id": user_id, "status": status}),)
            if status == "approved"
            else ()
        )
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("kyc", user_id, document),
            payload,
            events,
        )

    def verify_business(
        self, company_id: str, cnpj: str, legal_name: str
    ) -> SandboxResult:
        digits = "".join(char for char in cnpj if char.isdigit())
        status = (
            "approved"
            if len(digits) == 14 and not digits.endswith("0000")
            else "manual_review"
        )
        payload = {
            "company_id": company_id,
            "cnpj_hash": _digest("cnpj", digits),
            "legal_name_hash": _digest("legal_name", legal_name.casefold()),
            "provider_environment": "sandbox",
            "manual_review_required": status != "approved",
        }
        events = (
            (
                _event(
                    "business.company.approved",
                    {"company_id": company_id, "status": status},
                ),
            )
            if status == "approved"
            else ()
        )
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("kyb", company_id, digits),
            payload,
            events,
        )


class PspLedgerSandbox:
    provider_key = "finance_pix_psp"
    adapter = "local_psp_ledger_simulator"

    def authorize_pix(
        self, payment_id: str, payer_id: str, amount_brl: str, idempotency_key: str
    ) -> SandboxResult:
        amount = _money(amount_brl)
        status = "authorized" if amount > Decimal("0") else "rejected"
        payload = {
            "payment_id": payment_id,
            "payer_id": payer_id,
            "amount_brl": str(amount),
            "idempotency_key_hash": _digest("idempotency", idempotency_key),
            "end_to_end_id": _stable_id("pix", payment_id, idempotency_key),
            "provider_environment": "sandbox",
        }
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("psp", payment_id, idempotency_key),
            payload,
        )

    def create_escrow(
        self, escrow_id: str, payer_id: str, beneficiary_id: str, amount_brl: str
    ) -> SandboxResult:
        amount = _money(amount_brl)
        status = (
            "held"
            if amount > Decimal("0") and payer_id != beneficiary_id
            else "rejected"
        )
        payload = {
            "escrow_id": escrow_id,
            "payer_id": payer_id,
            "beneficiary_id": beneficiary_id,
            "amount_brl": str(amount),
            "provider_environment": "sandbox",
        }
        events = (
            (_event("payment.escrow.created", payload),) if status == "held" else ()
        )
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("escrow", escrow_id, amount),
            payload,
            events,
        )

    def release_escrow(self, escrow_id: str, amount_brl: str) -> SandboxResult:
        payload = {
            "escrow_id": escrow_id,
            "amount_brl": str(_money(amount_brl)),
            "provider_environment": "sandbox",
        }
        return SandboxResult(
            self.provider_key,
            self.adapter,
            "released",
            _stable_id("escrow_release", escrow_id, amount_brl),
            payload,
            (_event("payment.escrow.released", payload),),
        )

    def refund_payment(
        self,
        payment_id: str,
        amount_brl: str,
        idempotency_key: str,
        reason: str | None = None,
    ) -> SandboxResult:
        amount = _money(amount_brl)
        status = "refunded" if amount > Decimal("0") else "rejected"
        payload = {
            "payment_id": payment_id,
            "amount_brl": str(amount),
            "idempotency_key_hash": _digest("refund-idempotency", idempotency_key),
            "reason_hash": _digest("refund-reason", reason or "") if reason else None,
            "provider_environment": "sandbox",
        }
        events = (_event("payment.refunded", payload),) if status == "refunded" else ()
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("refund", payment_id, idempotency_key, amount),
            payload,
            events,
        )


class FiscalDocumentSandbox:
    provider_key = "fiscal_nfse_nfe"
    adapter = "local_fiscal_document_simulator"

    def issue_invoice(
        self, invoice_id: str, document_type: str, amount_brl: str, issuer_document: str
    ) -> SandboxResult:
        amount = _money(amount_brl)
        status = (
            "issued"
            if amount > Decimal("0") and document_type in {"nfse", "nfe", "receipt"}
            else "rejected"
        )
        payload = {
            "invoice_id": invoice_id,
            "document_type": document_type,
            "amount_brl": str(amount),
            "issuer_document_hash": _digest("issuer", issuer_document),
            "authorization_code": _digest("fiscal", invoice_id, document_type, amount)[
                :16
            ].upper(),
            "provider_environment": "sandbox",
        }
        events = (_event("erp.invoice.created", payload),) if status == "issued" else ()
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("fiscal", invoice_id, document_type),
            payload,
            events,
        )


def local_fiscal_document_simulator(
    document_id: str,
    amount_brl: str | None = None,
    company_id: str | None = None,
    action: str = "authorize",
    reason: str | None = None,
) -> dict[str, Any]:
    material = {
        "document_id": document_id,
        "amount_brl": str(_money(amount_brl or "0")),
        "company_id_hash": _digest("company", company_id or "unknown"),
        "action": action,
        "reason_hash": _digest("reason", reason or ""),
        "provider_environment": "sandbox",
    }
    status = "cancelled" if action == "cancel" else "authorized"
    return {
        "provider_key": FiscalDocumentSandbox.provider_key,
        "adapter": FiscalDocumentSandbox.adapter,
        "status": status,
        "reference_id": _stable_id("fiscal", document_id, action),
        "auth_code": _digest("fiscal", document_id, action, material["amount_brl"])[
            :16
        ].upper(),
        "payload": material,
        "audit": sandbox_audit_record(
            FiscalDocumentSandbox.provider_key,
            FiscalDocumentSandbox.adapter,
            status,
            _stable_id("fiscal", document_id, action),
            material,
        ),
    }


class CtpsSandbox:
    provider_key = "jobs_ctps_official"
    adapter = "local_ctps_pdf_importer_hash_only"

    def classify_pdf(self, resume_id: str, pdf_bytes: bytes) -> SandboxResult:
        sha256 = hashlib.sha256(pdf_bytes).hexdigest()
        status = (
            "hash_preserved" if pdf_bytes.startswith(b"%PDF") else "invalid_document"
        )
        payload = {
            "resume_id": resume_id,
            "sha256": sha256,
            "official_verification_status": "not_verified_externally",
            "provider_environment": "sandbox",
        }
        events = (
            (_event("jobs.resume.ctps_imported", payload),)
            if status == "hash_preserved"
            else ()
        )
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("ctps", resume_id, sha256),
            payload,
            events,
        )


class MapsRoutingSandbox:
    provider_key = "maps_routing_tracking"
    adapter = "local_distance_eta_calculator"

    def route(
        self,
        route_id: str,
        origin: dict[str, float],
        destination: dict[str, float],
        vehicle_type: str = "car",
    ) -> SandboxResult:
        lat1 = math.radians(float(origin["lat"]))
        lat2 = math.radians(float(destination["lat"]))
        delta_lat = lat2 - lat1
        delta_lng = math.radians(float(destination["lng"]) - float(origin["lng"]))
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
        )
        distance_km = Decimal(
            str(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
        ).quantize(Decimal("0.001"))
        speed = {
            "bicycle": Decimal("18"),
            "motorcycle": Decimal("32"),
            "car": Decimal("28"),
            "van": Decimal("24"),
            "truck": Decimal("20"),
        }.get(vehicle_type, Decimal("28"))
        eta_minutes = (distance_km / speed * Decimal("60")).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
        payload = {
            "route_id": route_id,
            "distance_km": str(distance_km),
            "eta_minutes": str(eta_minutes),
            "vehicle_type": vehicle_type,
            "provider_environment": "sandbox",
        }
        return SandboxResult(
            self.provider_key,
            self.adapter,
            "calculated",
            _stable_id("route", route_id, origin, destination),
            payload,
        )


class ClinicalConsentSandbox:
    provider_key = "health_telemedicine_prescription"
    adapter = "local_clinical_consent_simulator"

    def record_consent(
        self, patient_id: str, professional_id: str, purpose: str, ttl_days: int = 180
    ) -> SandboxResult:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(days=ttl_days)
        payload = {
            "patient_id": patient_id,
            "professional_id": professional_id,
            "purpose": purpose,
            "consent_hash": _digest(
                "health-consent", patient_id, professional_id, purpose, issued_at.date()
            ),
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "provider_environment": "sandbox",
        }
        return SandboxResult(
            self.provider_key,
            self.adapter,
            "active",
            _stable_id("health_consent", patient_id, purpose),
            payload,
        )


class ApiHubSandbox:
    provider_key = "api_hub_oauth_webhooks"
    adapter = "local_gateway_signature_and_api_key_validator"

    def sign_webhook(
        self, webhook_id: str, payload: dict[str, Any], secret: str
    ) -> SandboxResult:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        signature = hmac.new(
            secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        response = {
            "webhook_id": webhook_id,
            "payload_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "signature_sha256": signature,
            "provider_environment": "sandbox",
        }
        return SandboxResult(
            self.provider_key,
            self.adapter,
            "signed",
            _stable_id("webhook", webhook_id, response["payload_sha256"]),
            response,
        )

    def verify_api_key(self, api_key: str, allowed_hashes: set[str]) -> SandboxResult:
        salt = f"{self.provider_key}:{self.adapter}:api_key".encode("utf-8")
        api_key_hash = hashlib.pbkdf2_hmac(
            "sha256",
            api_key.encode("utf-8"),
            salt,
            210_000,
        ).hex()
        status = "accepted" if api_key_hash in allowed_hashes else "rejected"
        payload = {"api_key_hash": api_key_hash, "provider_environment": "sandbox"}
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("api_key", api_key_hash),
            payload,
        )


class SupplierCatalogSandbox:
    provider_key = "stock_supplier_catalog"
    adapter = "local_supplier_catalog_fixture"

    def import_product(
        self,
        supplier_id: str,
        external_sku: str,
        cost_brl: str,
        available_quantity: int,
    ) -> SandboxResult:
        cost = _money(cost_brl)
        status = (
            "available"
            if cost > Decimal("0") and available_quantity > 0
            else "unavailable"
        )
        payload = {
            "supplier_id": supplier_id,
            "external_sku": external_sku,
            "cost_brl": str(cost),
            "available_quantity": available_quantity,
            "provider_environment": "sandbox",
        }
        events = (
            (_event("stock.product.imported", payload),)
            if status == "available"
            else ()
        )
        return SandboxResult(
            self.provider_key,
            self.adapter,
            status,
            _stable_id("supplier_product", supplier_id, external_sku),
            payload,
            events,
        )


class AiAgentSandbox:
    provider_key = "ai_agent_superdesign"
    adapter = "local_mock_ai_response"

    def run_prompt(
        self, run_id: str, prompt: str, module: str = "ai_core"
    ) -> SandboxResult:
        payload = {
            "run_id": run_id,
            "module": module,
            "prompt_sha256": _digest("ai-prompt", prompt),
            "provider_environment": "sandbox",
            "cost_brl": "0.0000",
        }
        return SandboxResult(
            self.provider_key,
            self.adapter,
            "completed",
            _stable_id("ai_run", run_id, payload["prompt_sha256"]),
            payload,
            (_event("ai_core.model_run.completed", payload),),
        )


def sandbox_adapters() -> dict[str, object]:
    return {
        "identity_kyc_kyb": IdentityVerificationSandbox(),
        "finance_pix_psp": PspLedgerSandbox(),
        "fiscal_nfse_nfe": FiscalDocumentSandbox(),
        "jobs_ctps_official": CtpsSandbox(),
        "maps_routing_tracking": MapsRoutingSandbox(),
        "health_telemedicine_prescription": ClinicalConsentSandbox(),
        "api_hub_oauth_webhooks": ApiHubSandbox(),
        "stock_supplier_catalog": SupplierCatalogSandbox(),
        "ai_agent_superdesign": AiAgentSandbox(),
    }
