from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
import sys
from typing import Any, Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.dynamic_forms import DynamicFormValidationError
from shared.dynamic_forms_postgres_store import DynamicFormsPostgresStore
from shared.security import Actor, actor_from_headers, demand_mfa, demand_role


app = FastAPI(title="All-in-One Dynamic Forms", version="1.0.0")

DESIGN_ROLES = frozenset({"owner", "administrator", "form_designer"})
REVIEW_ROLES = frozenset({"owner", "administrator", "compliance_officer", "form_reviewer"})
PUBLISH_ROLES = frozenset({"owner", "administrator", "form_publisher"})
READ_ROLES = DESIGN_ROLES | REVIEW_ROLES | PUBLISH_ROLES | frozenset({"auditor"})
SUBMIT_ROLES = READ_ROLES | frozenset({"user", "form_user", "consumer", "employee"})


class DefinitionCreate(BaseModel):
    company_id: UUID | None = None
    module_id: str = Field(min_length=2, max_length=80, pattern=r"^[a-z][a-z0-9_]*$")
    business_context: str = Field(min_length=2, max_length=120, pattern=r"^[a-z][a-z0-9_.-]*$")
    name: str = Field(min_length=3, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    change_summary: str = Field(min_length=3, max_length=500)


class BlueprintReplace(BaseModel):
    blocks: list[dict[str, Any]] = Field(min_length=1, max_length=50)
    fields: list[dict[str, Any]] = Field(min_length=1, max_length=200)
    calculations: list[dict[str, Any]] = Field(default_factory=list, max_length=50)
    validations: list[dict[str, Any]] = Field(default_factory=list, max_length=500)
    visibility_rules: list[dict[str, Any]] = Field(default_factory=list, max_length=500)


class HomologationRequest(BaseModel):
    checklist: dict[str, Any] = Field(min_length=1)


class HomologationReview(BaseModel):
    result: str = Field(pattern=r"^(approved|changes_requested|rejected)$")
    notes: str | None = Field(default=None, max_length=4000)
    problems: list[dict[str, Any]] = Field(default_factory=list, max_length=200)
    corrections: list[dict[str, Any]] = Field(default_factory=list, max_length=200)
    evidence: dict[str, Any] = Field(default_factory=dict)


class PublicationRequest(BaseModel):
    environment: str = Field(pattern=r"^(development|homologation|production)$")
    rollout_policy: dict[str, Any] = Field(default_factory=dict)
    tenant_scope: dict[str, Any] = Field(min_length=1)
    channels: list[str] = Field(default_factory=lambda: ["web"], min_length=1, max_length=10)


class FormSubmissionRequest(BaseModel):
    values: dict[str, Any] = Field(min_length=1, max_length=200)
    context: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="web", pattern=r"^(web|mobile|api|import)$")


@lru_cache(maxsize=1)
def get_store() -> DynamicFormsPostgresStore:
    dsn = os.getenv("ALL_IN_ONE_DYNAMIC_FORMS_POSTGRES_DSN") or os.getenv("ALL_IN_ONE_POSTGRES_DSN")
    if not dsn:
        raise HTTPException(status_code=503, detail="PostgreSQL de formularios dinamicos nao configurado.")
    return DynamicFormsPostgresStore(dsn)


def tenant_actor(
    x_tenant_id: Annotated[UUID, Header(alias="X-Tenant-Id")],
    actor: Annotated[Actor, Depends(actor_from_headers)],
) -> tuple[str, Actor]:
    elevated = bool(actor.roles.intersection({"administrator", "platform_admin"}))
    if actor.business_id is not None and actor.business_id != x_tenant_id and not elevated:
        raise HTTPException(status_code=403, detail="Tenant informado diverge do contexto empresarial autenticado.")
    return str(x_tenant_id), actor


def demand_forms_access(actor: Actor, roles: frozenset[str], scope: str, action: str) -> None:
    demand_role(actor, roles, action)
    if not actor.roles.intersection({"owner", "administrator"}) and not actor.scopes.intersection({scope, "forms:manage"}):
        raise HTTPException(status_code=403, detail=f"Escopo {scope} obrigatorio para {action}.")


def idempotency_header(value: Annotated[str, Header(alias="X-Idempotency-Key", min_length=8, max_length=160)]) -> str:
    return value


@app.exception_handler(DynamicFormValidationError)
def handle_validation_error(_request: Any, exc: DynamicFormValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(KeyError)
def handle_not_found(_request: Any, exc: KeyError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc.args[0])})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "module": "dynamic_forms"}


@app.get("/catalog")
def list_catalog(
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
    domain: str | None = Query(default=None, min_length=2, max_length=80),
) -> list[dict[str, Any]]:
    _tenant_id, actor = context
    demand_forms_access(actor, READ_ROLES, "forms:read", "consultar catalogo de campos")
    return store.list_catalog(domain)


@app.get("/catalog/bindings")
def list_bindings(
    catalog_ids: Annotated[list[UUID], Query(min_length=1, max_length=200)],
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> list[dict[str, Any]]:
    _tenant_id, actor = context
    demand_forms_access(actor, READ_ROLES, "forms:read", "consultar bindings logicos")
    return store.list_bindings([str(item) for item in catalog_ids])


@app.post("/definitions", status_code=201)
def create_definition(
    body: DefinitionCreate,
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    idempotency_key: Annotated[str, Depends(idempotency_header)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context
    demand_forms_access(actor, DESIGN_ROLES, "forms:write", "criar formulario")
    if body.company_id and actor.business_id and body.company_id != actor.business_id and "administrator" not in actor.roles:
        raise HTTPException(status_code=403, detail="Empresa do formulario diverge da empresa autenticada.")
    return store.create_definition(
        tenant_id=tenant_id,
        company_id=str(body.company_id) if body.company_id else None,
        module_id=body.module_id,
        business_context=body.business_context,
        name=body.name,
        description=body.description,
        change_summary=body.change_summary,
        actor_user_id=str(actor.user_id),
        idempotency_key=idempotency_key,
    )


@app.get("/definitions")
def list_definitions(
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
    status: str | None = Query(default=None, pattern=r"^(draft|active|suspended|retired)$"),
) -> list[dict[str, Any]]:
    tenant_id, actor = context
    demand_forms_access(actor, READ_ROLES, "forms:read", "listar formularios")
    return store.list_definitions(tenant_id, status=status)


@app.get("/versions/{version_id}/blueprint")
def get_blueprint(
    version_id: UUID,
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context
    demand_forms_access(actor, READ_ROLES, "forms:read", "consultar blueprint")
    return store.get_blueprint(tenant_id, str(version_id))


@app.put("/versions/{version_id}/blueprint")
def replace_blueprint(
    version_id: UUID,
    body: BlueprintReplace,
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context
    demand_forms_access(actor, DESIGN_ROLES, "forms:write", "editar blueprint")
    return store.replace_blueprint(tenant_id, str(version_id), body.model_dump(), str(actor.user_id))


@app.post("/versions/{version_id}/homologations", status_code=201)
def request_homologation(
    version_id: UUID,
    body: HomologationRequest,
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    idempotency_key: Annotated[str, Depends(idempotency_header)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context
    demand_forms_access(actor, DESIGN_ROLES, "forms:write", "solicitar homologacao")
    return store.request_homologation(tenant_id, str(version_id), str(actor.user_id), body.checklist, idempotency_key)


@app.post("/homologations/{homologation_id}/review")
def review_homologation(
    homologation_id: UUID,
    body: HomologationReview,
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    idempotency_key: Annotated[str, Depends(idempotency_header)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context
    demand_forms_access(actor, REVIEW_ROLES, "forms:review", "homologar formulario")
    demand_mfa(actor, "homologar formulario")
    return store.review_homologation(
        tenant_id,
        str(homologation_id),
        str(actor.user_id),
        body.result,
        body.notes,
        body.problems,
        body.corrections,
        body.evidence,
        idempotency_key,
    )


@app.post("/versions/{version_id}/publish", status_code=201)
def publish_version(
    version_id: UUID,
    body: PublicationRequest,
    context: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    idempotency_key: Annotated[str, Depends(idempotency_header)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context
    demand_forms_access(actor, PUBLISH_ROLES, "forms:publish", "publicar formulario")
    demand_mfa(actor, "publicar formulario")
    return store.publish_version(
        tenant_id,
        str(version_id),
        str(actor.user_id),
        body.environment,
        body.rollout_policy,
        body.tenant_scope,
        body.channels,
        idempotency_key,
    )


@app.post("/forms/{definition_id}/submissions", status_code=201)
def submit_form(
    definition_id: UUID,
    body: FormSubmissionRequest,
    context_actor: Annotated[tuple[str, Actor], Depends(tenant_actor)],
    idempotency_key: Annotated[str, Depends(idempotency_header)],
    store: Annotated[DynamicFormsPostgresStore, Depends(get_store)],
) -> dict[str, Any]:
    tenant_id, actor = context_actor
    demand_forms_access(actor, SUBMIT_ROLES, "forms:submit", "enviar formulario")
    return store.submit_form(
        tenant_id,
        str(definition_id),
        str(actor.user_id),
        body.values,
        body.context,
        body.source,
        idempotency_key,
    )
