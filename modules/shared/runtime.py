from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query, Response
from pydantic import BaseModel, Field

from .calculators import (
    CommissionRequest,
    DeliveryQuoteRequest,
    MobilityFareRequest,
    delivery_quote,
    marketplace_commission,
    mobility_fare,
)
from .domain_rules import (
    APPROVER_ROLES,
    MODULE_ENTITIES,
    PRIMARY_RESOURCE,
    ResourceRule,
    can_read_sensitive,
    check_payload,
    event_for_create,
    rule_for,
)
from .security import Actor, actor_from_headers, demand_active_business_recruiter, demand_mfa, demand_role
from .store import DuplicateValueError, SQLiteStore


class ResourceCreate(BaseModel):
    user_id: UUID
    entity_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ResourcePatch(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)


class ActionPayload(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
    payload: dict[str, Any] = Field(default_factory=dict)


class AuditPayload(BaseModel):
    action: str = Field(min_length=3, max_length=80)
    resource_type: str = Field(min_length=2, max_length=80)
    resource_id: UUID
    payload: dict[str, Any] = Field(default_factory=dict)


class IdentityRegistration(BaseModel):
    full_name: str = Field(min_length=3, max_length=200)
    cpf_document: str = Field(min_length=5, max_length=32)
    email: str = Field(min_length=5, max_length=254)
    phone_e164: str = Field(min_length=8, max_length=20)
    face_hash: str = Field(min_length=16, max_length=256)
    terms_accepted_at: str = Field(min_length=10, max_length=40)
    lgpd_consent_at: str = Field(min_length=10, max_length=40)


# Compatibility bodies for integrations using the initial baseline routes.
class CreatePayload(ResourceCreate):
    status: str = Field(default="draft", max_length=40)


class PatchPayload(ResourcePatch):
    status: str | None = Field(default=None, max_length=40)


class DecisionPayload(BaseModel):
    id: UUID
    reason: str = Field(min_length=3, max_length=500)


TRANSACTIONAL_RESOURCES = {
    ("finance", "ledger_entries"),
    ("finance", "escrows"),
    ("marketplace", "orders"),
    ("delivery", "delivery_requests"),
    ("services", "service_contracts"),
    ("mobility", "rides"),
}


def _database_path(module_name: str) -> str:
    directory = os.getenv("ALL_IN_ONE_STORAGE_DIR")
    if not directory:
        return ":memory:"
    return str(Path(directory) / f"{module_name}.db")


def _authorize_owner_or_operator(actor: Actor, user_id: UUID, action: str) -> None:
    if actor.user_id != user_id and not actor.roles.intersection(APPROVER_ROLES):
        raise HTTPException(status_code=403, detail=f"Ator nao autorizado para {action} em recurso de outro usuario.")


def _expose(item: dict[str, Any], actor: Actor, rule: ResourceRule, module_name: str) -> dict[str, Any]:
    if module_name == "jobs" and rule.sensitive and actor.user_id != UUID(item["user_id"]):
        raise HTTPException(status_code=403, detail="Curriculo de terceiro exige consulta Business auditada.")
    if rule.sensitive and actor.user_id != UUID(item["user_id"]) and not can_read_sensitive(module_name, actor.roles):
        raise HTTPException(status_code=403, detail="Leitura de dado sensivel nao autorizada.")
    return item


def create_module_app(module_name: str, version: str = "0.2.0") -> FastAPI:
    if module_name not in MODULE_ENTITIES:
        raise ValueError(f"Modulo desconhecido: {module_name}")
    app = FastAPI(title=f"All-in-One {module_name}", version=version)
    store = SQLiteStore(module_name, _database_path(module_name))
    legacy_rule = ResourceRule()

    def fetch(resource_type: str, resource_id: UUID) -> dict[str, Any]:
        item = store.get(resource_type, str(resource_id))
        if item is None:
            raise HTTPException(status_code=404, detail="Registro nao encontrado.")
        return item

    def create_secured(
        resource_type: str,
        body: ResourceCreate,
        actor: Actor,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        rule = rule_for(module_name, resource_type)
        _authorize_owner_or_operator(actor, body.user_id, "create")
        payload = dict(body.payload)
        if module_name == "jobs" and resource_type in {"resumes", "employment_records", "applications"} and actor.user_id != body.user_id:
            raise HTTPException(status_code=403, detail="Somente o titular pode alterar sua jornada de candidato.")
        if module_name == "jobs" and resource_type in {"resume_documents", "resume_access_logs"}:
            raise HTTPException(status_code=422, detail="Recurso Jobs criado somente por fluxo auditado interno.")
        if module_name == "jobs" and resource_type == "employment_records":
            if payload.get("source_type") not in (None, "user_declared"):
                raise HTTPException(status_code=422, detail="Origem documental somente e criada pelo importador CTPS PDF.")
            try:
                resume_id = UUID(str(payload.get("resume_id")))
            except ValueError:
                raise HTTPException(status_code=422, detail="resume_id valido e obrigatorio.") from None
            resume = fetch("resumes", resume_id)
            _authorize_owner_or_operator(actor, UUID(resume["user_id"]), "adicionar experiencia")
            if UUID(resume["user_id"]) != body.user_id:
                raise HTTPException(status_code=422, detail="Experiencia deve pertencer ao dono do curriculo.")
            payload.update(
                {
                    "source_type": "user_declared",
                    "evidence_status": "self_declared_unverified",
                    "official_verification_status": "not_in_ctps_import",
                    "visible_to_recruiter": True,
                }
            )
        if module_name == "jobs" and resource_type == "job_postings":
            demand_active_business_recruiter(actor, "publicar vagas", "jobs:manage")
            if str(payload.get("company_id")) != str(actor.business_id):
                raise HTTPException(status_code=403, detail="Vaga deve pertencer a empresa Business autenticada.")
        if module_name == "jobs" and resource_type == "applications":
            try:
                resume = fetch("resumes", UUID(str(payload.get("resume_id"))))
                posting = fetch("job_postings", UUID(str(payload.get("job_posting_id"))))
            except ValueError:
                raise HTTPException(status_code=422, detail="Vaga e curriculo validos sao obrigatorios.") from None
            if UUID(resume["user_id"]) != body.user_id:
                raise HTTPException(status_code=403, detail="Candidatura exige curriculo do proprio usuario.")
            if posting["status"] != "published":
                raise HTTPException(status_code=409, detail="Candidatura exige vaga publicada.")
        if (module_name, resource_type) in TRANSACTIONAL_RESOURCES and not idempotency_key:
            raise HTTPException(status_code=422, detail="X-Idempotency-Key obrigatorio para operacao transacional.")
        check_payload(rule, payload)
        try:
            return store.create(
                resource_type,
                str(body.user_id),
                str(body.entity_id) if body.entity_id else None,
                rule.initial_status,
                payload,
                str(actor.user_id),
                rule.unique_fields,
                event_for_create(module_name, resource_type),
                idempotency_key,
            )
        except DuplicateValueError as exc:
            raise HTTPException(status_code=409, detail=f"Valor unico ja utilizado: {exc}.") from None

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "module": module_name, "storage": "sqlite_contract_store"}

    @app.get("/version")
    def get_version() -> dict[str, str]:
        return {"module": module_name, "version": version}

    @app.get("/status")
    def status(actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
        records, audits, events = store.metrics()
        return {
            "module": module_name,
            "state": "domain_engine_active",
            "records": records,
            "audit_events": audits,
            "outbox_events": events,
            "actor": str(actor.user_id),
        }

    @app.get("/metrics")
    def metrics() -> Response:
        records, audits, events = store.metrics()
        output = (
            f'all_in_one_records{{module="{module_name}"}} {records}\n'
            f'all_in_one_audit_events{{module="{module_name}"}} {audits}\n'
            f'all_in_one_domain_events{{module="{module_name}"}} {events}\n'
        )
        return Response(output, media_type="text/plain; version=0.0.4")

    @app.get("/catalog")
    def catalog() -> dict[str, Any]:
        return {"module": module_name, "resources": list(MODULE_ENTITIES[module_name]), "primary_resource": PRIMARY_RESOURCE[module_name]}

    if module_name == "identity":
        @app.post("/registrations", status_code=201)
        def register_user(body: IdentityRegistration) -> dict[str, Any]:
            user_id = str(uuid4())
            payload = body.model_dump()
            rule = rule_for("identity", "users")
            check_payload(rule, payload)
            try:
                return store.create(
                    "users",
                    user_id,
                    None,
                    rule.initial_status,
                    payload,
                    user_id,
                    rule.unique_fields,
                    "identity.user.created",
                    None,
                )
            except DuplicateValueError as exc:
                raise HTTPException(status_code=409, detail=f"Cadastro ja existente: {exc}.") from None

    @app.post("/resources/{resource_type}", status_code=201)
    def create_resource(
        resource_type: str,
        body: ResourceCreate,
        actor: Actor = Depends(actor_from_headers),
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    ) -> dict[str, Any]:
        return create_secured(resource_type, body, actor, x_idempotency_key)

    @app.get("/resources/{resource_type}")
    def list_resources(
        resource_type: str,
        user_id: UUID | None = None,
        actor: Actor = Depends(actor_from_headers),
    ) -> list[dict[str, Any]]:
        rule = rule_for(module_name, resource_type)
        if user_id and actor.user_id != user_id and not actor.roles.intersection(APPROVER_ROLES):
            raise HTTPException(status_code=403, detail="Consulta de outro usuario nao autorizada.")
        rows = store.list(resource_type, str(user_id) if user_id else str(actor.user_id))
        return [_expose(item, actor, rule, module_name) for item in rows]

    @app.get("/resources/{resource_type}/{resource_id}")
    def get_resource(
        resource_type: str,
        resource_id: UUID,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        rule = rule_for(module_name, resource_type)
        return _expose(fetch(resource_type, resource_id), actor, rule, module_name)

    @app.patch("/resources/{resource_type}/{resource_id}")
    def patch_resource(
        resource_type: str,
        resource_id: UUID,
        body: ResourcePatch,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        rule = rule_for(module_name, resource_type)
        if rule.immutable:
            raise HTTPException(status_code=409, detail="Recurso append-only nao aceita atualizacao.")
        item = fetch(resource_type, resource_id)
        if module_name == "jobs" and resource_type in {"resumes", "employment_records", "applications"} and actor.user_id != UUID(item["user_id"]):
            raise HTTPException(status_code=403, detail="Somente o titular pode alterar sua jornada de candidato.")
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "update")
        merged = {**item["payload"], **body.payload}
        check_payload(rule, merged)
        return store.update(item, merged, item["status"], str(actor.user_id), "update")

    @app.delete("/resources/{resource_type}/{resource_id}", status_code=204)
    def delete_resource(
        resource_type: str,
        resource_id: UUID,
        actor: Actor = Depends(actor_from_headers),
    ) -> Response:
        rule = rule_for(module_name, resource_type)
        if rule.immutable or rule.sensitive:
            raise HTTPException(status_code=409, detail="Recurso protegido exige retencao e nao pode ser excluido.")
        item = fetch(resource_type, resource_id)
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "delete")
        store.soft_delete(item, str(actor.user_id))
        return Response(status_code=204)

    @app.post("/resources/{resource_type}/{resource_id}/actions/{action}")
    def transition_resource(
        resource_type: str,
        resource_id: UUID,
        action: str,
        body: ActionPayload,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        rule = rule_for(module_name, resource_type)
        transition = rule.transitions.get(action)
        if transition is None:
            raise HTTPException(status_code=422, detail=f"Acao nao suportada: {action}.")
        item = fetch(resource_type, resource_id)
        if module_name == "jobs" and resource_type == "job_postings":
            demand_active_business_recruiter(actor, "gerenciar vagas", "jobs:manage")
            if str(item["payload"].get("company_id")) != str(actor.business_id):
                raise HTTPException(status_code=403, detail="Vaga pertence a outra empresa Business.")
        if module_name == "jobs" and resource_type == "applications" and action != "withdraw":
            demand_active_business_recruiter(actor, "avaliar candidaturas", "jobs:manage")
            posting = fetch("job_postings", UUID(str(item["payload"].get("job_posting_id"))))
            if str(posting["payload"].get("company_id")) != str(actor.business_id):
                raise HTTPException(status_code=403, detail="Candidatura pertence a outra empresa Business.")
        if item["status"] not in transition.source:
            raise HTTPException(status_code=409, detail=f"Transicao {action} invalida a partir de {item['status']}.")
        if transition.roles:
            demand_role(actor, transition.roles, action)
        else:
            _authorize_owner_or_operator(actor, UUID(item["user_id"]), action)
        if transition.requires_mfa:
            demand_mfa(actor, action)
        payload = {**item["payload"], **body.payload, "decision_reason": body.reason}
        check_payload(rule, payload)
        return store.update(item, payload, transition.target, str(actor.user_id), action, transition.event)

    @app.get("/audit/events")
    def audit_events(actor: Actor = Depends(actor_from_headers)) -> list[dict[str, Any]]:
        demand_role(actor, APPROVER_ROLES, "audit")
        return store.audit_log()

    @app.get("/events/outbox")
    def outbox(actor: Actor = Depends(actor_from_headers)) -> list[dict[str, Any]]:
        demand_role(actor, APPROVER_ROLES, "outbox")
        return store.outbox()

    if module_name == "delivery":
        @app.post("/pricing/quote")
        def calculate_delivery_quote(body: DeliveryQuoteRequest, actor: Actor = Depends(actor_from_headers)) -> dict[str, str]:
            return delivery_quote(body)

    if module_name == "mobility":
        @app.post("/pricing/fare")
        def calculate_mobility_fare(body: MobilityFareRequest, actor: Actor = Depends(actor_from_headers)) -> dict[str, str]:
            return mobility_fare(body)

    if module_name == "marketplace":
        @app.post("/pricing/commission")
        def calculate_marketplace_commission(body: CommissionRequest, actor: Actor = Depends(actor_from_headers)) -> dict[str, str]:
            return marketplace_commission(body)

    if module_name == "jobs":
        from .ctps_import import extract_ctps_pdf

        def assemble_resume(resume: dict[str, Any], for_recruiter: bool = False) -> dict[str, Any]:
            records = [
                item
                for item in store.list("employment_records", resume["user_id"])
                if item["payload"].get("resume_id") == resume["id"]
            ]
            documents = [
                item
                for item in store.list("resume_documents", resume["user_id"])
                if item["payload"].get("resume_id") == resume["id"]
            ]
            if for_recruiter:
                documents = [
                    {
                        **item,
                        "payload": {
                            "document_type": item["payload"].get("document_type"),
                            "evidence_status": item["payload"].get("evidence_status"),
                            "official_verification_status": item["payload"].get("official_verification_status"),
                            "extraction_status": item["payload"].get("extraction_status"),
                        },
                    }
                    for item in documents
                ]
            return {
                "resume": resume,
                "employment_records": {
                    "validated_by_document_import": [
                        item for item in records if item["payload"].get("evidence_status") == "validated_by_document_import"
                    ],
                    "self_declared_unverified": [
                        item for item in records if item["payload"].get("evidence_status") == "self_declared_unverified"
                    ],
                },
                "documents": documents,
                "provenance_legend": {
                    "validated_by_document_import": "Extraido de PDF da CTPS Digital importado e preservado por hash.",
                    "self_declared_unverified": "Declarado pelo usuario e nao localizado no documento importado.",
                    "official_verification_status": "Validacao externa oficial nao executada pelo importador.",
                },
            }

        @app.post("/resumes/{resume_id}/imports/ctps-digital", status_code=201)
        def import_ctps_digital(
            resume_id: UUID,
            document: bytes = Body(media_type="application/pdf"),
            actor: Actor = Depends(actor_from_headers),
        ) -> dict[str, Any]:
            resume = fetch("resumes", resume_id)
            if actor.user_id != UUID(resume["user_id"]):
                raise HTTPException(status_code=403, detail="Somente o titular pode importar sua CTPS Digital.")
            if len(document) > 15 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="PDF excede limite de 15 MB.")
            try:
                result = extract_ctps_pdf(document)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from None
            document_payload = {key: value for key, value in result.items() if key != "employment_records"}
            document_payload["resume_id"] = str(resume_id)
            evidence = store.create(
                "resume_documents",
                resume["user_id"],
                resume["entity_id"],
                "imported",
                document_payload,
                str(actor.user_id),
                ("sha256",),
                "jobs.resume.ctps_imported",
                f"ctps:{result['sha256']}",
            )
            imported: list[dict[str, Any]] = []
            for index, extracted in enumerate(result["employment_records"]):
                payload = {
                    **extracted,
                    "resume_id": str(resume_id),
                    "source_document_id": evidence["id"],
                    "visible_to_recruiter": True,
                }
                imported.append(
                    store.create(
                        "employment_records",
                        resume["user_id"],
                        resume["entity_id"],
                        "active",
                        payload,
                        str(actor.user_id),
                        (),
                        "jobs.employment.ctps_imported",
                        f"ctps:{result['sha256']}:{index}",
                    )
                )
            return {
                "document": evidence,
                "imported_employment_records": imported,
                "extraction_status": result["extraction_status"],
                "display_badge": "Validado por importacao CTPS Digital",
                "official_verification_status": "not_verified_externally",
            }

        @app.get("/resumes/{resume_id}/complete")
        def own_complete_resume(resume_id: UUID, actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
            resume = fetch("resumes", resume_id)
            if actor.user_id != UUID(resume["user_id"]):
                raise HTTPException(status_code=403, detail="Use a consulta Business auditada para curriculo de terceiro.")
            return assemble_resume(resume)

        @app.get("/vacancies")
        def vacancies(q: str | None = Query(default=None, max_length=100)) -> list[dict[str, Any]]:
            terms = q.casefold() if q else None
            rows = [row for row in store.list("job_postings") if row["status"] == "published"]
            if terms:
                rows = [
                    row for row in rows
                    if terms in str(row["payload"].get("title", "")).casefold()
                    or terms in str(row["payload"].get("description", "")).casefold()
                ]
            return rows

        @app.get("/recruiting/resumes")
        def candidate_resumes(
            q: str | None = Query(default=None, max_length=100),
            actor: Actor = Depends(actor_from_headers),
        ) -> list[dict[str, Any]]:
            demand_active_business_recruiter(actor)
            terms = q.casefold() if q else None
            resumes = [
                item for item in store.list("resumes")
                if item["payload"].get("recruiter_visibility") == "business_recruiters"
            ]
            if terms:
                resumes = [
                    item for item in resumes
                    if terms in str(item["payload"].get("headline", "")).casefold()
                    or terms in str(item["payload"].get("skills", "")).casefold()
                ]
            store.audit_external(
                str(actor.user_id),
                "recruiter_search",
                "resumes",
                str(actor.business_id),
                {"query": q, "business_id": str(actor.business_id)},
            )
            return resumes

        @app.get("/recruiting/resumes/{resume_id}")
        def recruiter_resume_view(
            resume_id: UUID,
            purpose: str = Query(min_length=3, max_length=200),
            actor: Actor = Depends(actor_from_headers),
        ) -> dict[str, Any]:
            demand_active_business_recruiter(actor)
            resume = fetch("resumes", resume_id)
            if resume["payload"].get("recruiter_visibility") != "business_recruiters":
                raise HTTPException(status_code=403, detail="Usuario nao autorizou visibilidade a recrutadores.")
            store.create(
                "resume_access_logs",
                resume["user_id"],
                str(actor.business_id),
                "recorded",
                {"resume_id": str(resume_id), "business_id": str(actor.business_id), "purpose": purpose},
                str(actor.user_id),
                (),
                "jobs.resume.viewed",
                None,
            )
            return assemble_resume(resume, for_recruiter=True)

    # Backward-compatible baseline endpoints. New clients should use /resources/*.
    @app.post("/create", status_code=201, deprecated=True)
    def create_record(
        body: CreatePayload,
        actor: Actor = Depends(actor_from_headers),
        x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    ) -> dict[str, Any]:
        _authorize_owner_or_operator(actor, body.user_id, "create")
        return store.create(
            "records",
            str(body.user_id),
            str(body.entity_id) if body.entity_id else None,
            body.status,
            body.payload,
            str(actor.user_id),
            (),
            f"{module_name}.record.created",
            x_idempotency_key,
        )

    @app.get("/list", deprecated=True)
    def list_records(user_id: UUID | None = None, actor: Actor = Depends(actor_from_headers)) -> list[dict[str, Any]]:
        _authorize_owner_or_operator(actor, user_id or actor.user_id, "list")
        return store.list("records", str(user_id) if user_id else str(actor.user_id))

    @app.post("/approve", deprecated=True)
    def approve(
        body: DecisionPayload,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        item = fetch("records", body.id)
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "approve")
        return store.update(item, item["payload"], "approved", str(actor.user_id), "approve")

    @app.post("/reject", deprecated=True)
    def reject(
        body: DecisionPayload,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        item = fetch("records", body.id)
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "reject")
        return store.update(item, item["payload"], "rejected", str(actor.user_id), "reject")

    @app.post("/audit", status_code=201, deprecated=True)
    def audit(
        body: AuditPayload,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        demand_role(actor, APPROVER_ROLES, "audit")
        return store.audit_external(str(actor.user_id), body.action, body.resource_type, str(body.resource_id), body.payload)

    @app.get("/{resource_id}", deprecated=True)
    def get_record(resource_id: UUID, actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
        item = fetch("records", resource_id)
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "read")
        return item

    @app.patch("/{resource_id}", deprecated=True)
    def patch_record(
        resource_id: UUID,
        body: PatchPayload,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        item = fetch("records", resource_id)
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "update")
        return store.update(
            item,
            {**item["payload"], **body.payload},
            body.status or item["status"],
            str(actor.user_id),
            "update",
        )

    @app.delete("/{resource_id}", status_code=204, deprecated=True)
    def delete_record(resource_id: UUID, actor: Actor = Depends(actor_from_headers)) -> Response:
        item = fetch("records", resource_id)
        _authorize_owner_or_operator(actor, UUID(item["user_id"]), "delete")
        store.soft_delete(item, str(actor.user_id))
        return Response(status_code=204)

    return app
