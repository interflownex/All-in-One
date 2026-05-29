from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import re
from typing import Any

from fastapi import HTTPException


CPF_DOCUMENT = re.compile(r"^[0-9A-Za-z.-]{5,32}$")
PHONE_E164 = re.compile(r"^\+[1-9][0-9]{7,14}$")
OFF_PLATFORM_PATTERNS = (
    re.compile(r"\b(?:whats?app|telegram|instagram|facebook|pix)\b", re.IGNORECASE),
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE),
    re.compile(r"https?://|www\.", re.IGNORECASE),
    re.compile(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?\d{4,5}[-\s]?\d{4}"),
)
APPROVER_ROLES = frozenset(
    {"owner", "legal_representative", "administrator", "compliance_officer", "auditor"}
)
SENSITIVE_ROLES = frozenset(
    {"owner", "administrator", "compliance_officer", "data_protection_officer", "auditor"}
)
MEDICAL_ROLES = frozenset({"medical_admin", "doctor", "nurse", "compliance_officer"})
RECRUITER_ROLES = frozenset({"owner", "administrator", "hr_manager", "recruiter", "auditor"})


@dataclass(frozen=True)
class Transition:
    source: frozenset[str]
    target: str
    roles: frozenset[str] = field(default_factory=frozenset)
    requires_mfa: bool = False
    event: str | None = None


@dataclass(frozen=True)
class ResourceRule:
    required_fields: tuple[str, ...] = ()
    unique_fields: tuple[str, ...] = ()
    initial_status: str = "draft"
    protected_content: bool = False
    immutable: bool = False
    sensitive: bool = False
    monetary_fields: tuple[str, ...] = ()
    transitions: dict[str, Transition] = field(default_factory=dict)


MODULE_ENTITIES: dict[str, tuple[str, ...]] = {
    "identity": ("users", "kyc_records", "business_profiles", "consents", "audit_logs"),
    "business": ("companies", "branches", "company_documents", "user_company_memberships"),
    "permissions": ("roles", "permissions", "user_roles", "access_policies", "approval_limits"),
    "finance": ("wallets", "ledger_entries", "escrows", "splits", "invoices"),
    "marketplace": ("stores", "products", "carts", "orders", "reviews", "disputes"),
    "stock": ("suppliers", "catalog_products", "price_rules", "supplier_orders"),
    "delivery": ("delivery_requests", "quotes", "assignments", "proofs", "insurance_options"),
    "riders": ("rider_profiles", "rider_documents", "vehicles", "rider_reviews"),
    "services": ("providers", "visits", "quotes", "service_contracts", "evidence"),
    "mobility": ("rides", "routes", "stops", "tickets", "fare_rules"),
    "jobs": ("resumes", "employment_records", "resume_documents", "job_postings", "applications", "resume_access_logs"),
    "erp": ("accounts", "payables", "receivables", "cost_centers", "fiscal_documents"),
    "wms": ("warehouses", "bins", "inventory", "picking_waves", "shipments"),
    "tms": ("carriers", "freights", "routes", "proofs_of_delivery", "freight_audits"),
    "crm": ("leads", "opportunities", "activities", "campaigns"),
    "bpm": ("processes", "workflow_instances", "tasks", "sla_policies"),
    "document": ("folders", "documents", "versions", "retention_policies"),
    "hr": ("employees", "payroll_runs", "candidates", "courses", "occupational_records"),
    "health": ("patients", "appointments", "medical_records", "prescriptions", "beds"),
    "vision": ("devices", "streams", "recordings", "motion_alerts"),
    "legal": ("cases", "deadlines", "hearings", "legal_contracts"),
    "property": ("properties", "units", "leases", "assemblies", "maintenance_orders"),
    "bi": ("datasets", "dashboards", "indicators", "exports"),
    "ai_core": ("ai_memories", "moderation_decisions", "model_runs"),
    "api_hub": ("api_clients", "api_keys", "webhooks", "integration_runs"),
}
PRIMARY_RESOURCE = {module: resources[0] for module, resources in MODULE_ENTITIES.items()}


def review_flow(prefix: str) -> dict[str, Transition]:
    return {
        "submit": Transition(frozenset({"draft", "pending_documents"}), "pending_review", event=f"{prefix}.submitted"),
        "approve": Transition(
            frozenset({"draft", "pending_review", "pending_validation", "under_review"}),
            "approved",
            APPROVER_ROLES,
            True,
            f"{prefix}.approved",
        ),
        "activate": Transition(frozenset({"approved"}), "active", APPROVER_ROLES, True),
        "reject": Transition(
            frozenset({"draft", "pending_review", "pending_validation", "under_review"}),
            "rejected",
            APPROVER_ROLES,
            True,
            f"{prefix}.rejected",
        ),
        "suspend": Transition(frozenset({"approved", "active"}), "suspended", APPROVER_ROLES, True),
    }


def lifecycle_flow(prefix: str) -> dict[str, Transition]:
    return {
        "submit": Transition(frozenset({"draft"}), "pending_review", event=f"{prefix}.submitted"),
        "approve": Transition(frozenset({"draft", "pending_review"}), "approved", APPROVER_ROLES, True),
        "cancel": Transition(frozenset({"draft", "pending_review", "approved", "active"}), "cancelled", event=f"{prefix}.cancelled"),
        "complete": Transition(frozenset({"approved", "active", "in_progress"}), "completed", event=f"{prefix}.completed"),
    }


RULE_OVERRIDES: dict[tuple[str, str], ResourceRule] = {
    ("identity", "users"): ResourceRule(
        ("full_name", "email", "password_hash"),
        ("email", "document_cpf"),
        "PENDING_KYC",
        sensitive=True,
        transitions={
            "verify": Transition(frozenset({"PENDING_KYC"}), "ACTIVE", APPROVER_ROLES, True, "identity.user.verified"),
            "suspend": Transition(frozenset({"ACTIVE"}), "SUSPENDED", APPROVER_ROLES, True),
            "block": Transition(frozenset({"PENDING_KYC", "ACTIVE", "SUSPENDED"}), "BLOCKED", APPROVER_ROLES, True),
        },
    ),
    ("identity", "kyc_records"): ResourceRule(
        ("user_id", "biometry_hash"),
        initial_status="PROCESSING",
        sensitive=True,
        transitions={
            "approve": Transition(frozenset({"PROCESSING"}), "APPROVED", APPROVER_ROLES, True, "identity.kyc.approved"),
            "reject": Transition(frozenset({"PROCESSING"}), "REJECTED", APPROVER_ROLES, True, "identity.kyc.rejected"),
        },
    ),
    ("identity", "business_profiles"): ResourceRule(
        ("owner_user_id", "legal_name", "document_cnpj"),
        ("document_cnpj",),
        "PENDING_KYB",
        transitions={
            "approve": Transition(frozenset({"PENDING_KYB"}), "ACTIVE", APPROVER_ROLES, True, "identity.kyb.approved"),
            "reject": Transition(frozenset({"PENDING_KYB"}), "REJECTED", APPROVER_ROLES, True, "identity.kyb.rejected"),
        },
    ),
    ("identity", "consents"): ResourceRule(
        ("user_id", "document_version", "consent_type"),
        initial_status="accepted",
        immutable=True,
    ),
    ("business", "companies"): ResourceRule(
        ("cnpj", "root_cnpj", "legal_name", "legal_representative_user_id"),
        ("cnpj",),
        "pending_validation",
        sensitive=True,
        transitions=review_flow("business.company"),
    ),
    ("permissions", "roles"): ResourceRule(("name",), ("name",), "active"),
    ("permissions", "approval_limits"): ResourceRule(
        ("scope", "limit_brl"), monetary_fields=("limit_brl",), initial_status="active"
    ),
    ("finance", "wallets"): ResourceRule(("wallet_type",), initial_status="active", sensitive=True),
    ("finance", "ledger_entries"): ResourceRule(
        ("wallet_id", "currency", "idempotency_key"),
        ("idempotency_key",),
        "posted",
        immutable=True,
        sensitive=True,
        monetary_fields=("amount_brl", "amount_nex"),
    ),
    ("finance", "escrows"): ResourceRule(
        ("wallet_id", "beneficiary_user_id", "amount_brl"),
        initial_status="created",
        sensitive=True,
        monetary_fields=("amount_brl",),
        transitions={
            "authorize": Transition(frozenset({"created"}), "authorized", APPROVER_ROLES, True),
            "capture": Transition(frozenset({"authorized"}), "held", APPROVER_ROLES, True, "payment.escrow.created"),
            "release": Transition(frozenset({"held"}), "released", APPROVER_ROLES, True, "payment.escrow.released"),
            "refund": Transition(frozenset({"authorized", "held", "disputed"}), "refunded", APPROVER_ROLES, True, "payment.refunded"),
            "dispute": Transition(frozenset({"held"}), "disputed", event="payment.escrow.disputed"),
        },
    ),
    ("marketplace", "stores"): ResourceRule(
        ("company_id", "company_status", "name"),
        initial_status="pending_validation",
        protected_content=True,
        transitions=review_flow("marketplace.store"),
    ),
    ("marketplace", "products"): ResourceRule(
        ("store_id", "sku", "name", "price_brl"),
        ("sku",),
        protected_content=True,
        monetary_fields=("price_brl",),
        transitions=lifecycle_flow("marketplace.product"),
    ),
    ("marketplace", "orders"): ResourceRule(
        ("store_id", "total_brl", "escrow_id"),
        initial_status="created",
        protected_content=True,
        monetary_fields=("total_brl",),
        transitions={
            "pay": Transition(frozenset({"created"}), "paid", event="marketplace.order.paid"),
            "deliver": Transition(frozenset({"paid", "shipped"}), "delivered", event="marketplace.order.delivered"),
            "cancel": Transition(frozenset({"created", "paid"}), "cancelled", event="marketplace.order.cancelled"),
        },
    ),
    ("stock", "suppliers"): ResourceRule(
        ("company_id", "company_status"), initial_status="pending_validation", transitions=review_flow("stock.supplier")
    ),
    ("stock", "catalog_products"): ResourceRule(
        ("supplier_id", "external_sku", "cost_brl", "markup_percent"),
        ("external_sku",),
        monetary_fields=("cost_brl",),
    ),
    ("delivery", "delivery_requests"): ResourceRule(
        ("service_type", "origin", "destination"),
        initial_status="created",
        protected_content=True,
        monetary_fields=("quoted_brl",),
        transitions={
            "assign": Transition(frozenset({"created", "quoted"}), "assigned", event="delivery.rider.assigned"),
            "pickup": Transition(frozenset({"assigned"}), "picked_up", event="delivery.picked_up"),
            "complete": Transition(frozenset({"picked_up"}), "completed", event="delivery.completed"),
            "cancel": Transition(frozenset({"created", "quoted", "assigned"}), "cancelled", event="delivery.cancelled"),
        },
    ),
    ("riders", "rider_profiles"): ResourceRule(
        ("cnh_number_hash", "cnh_category", "wallet_id"),
        initial_status="pending_documents",
        sensitive=True,
        transitions=review_flow("rider"),
    ),
    ("riders", "vehicles"): ResourceRule(
        ("rider_profile_id", "type", "license_plate"), initial_status="pending_review", transitions=review_flow("rider.vehicle")
    ),
    ("services", "providers"): ResourceRule(
        ("category",), initial_status="pending_review", protected_content=True, transitions=review_flow("services.provider")
    ),
    ("services", "service_contracts"): ResourceRule(
        ("provider_user_id", "escrow_id", "visit_price_brl"),
        protected_content=True,
        monetary_fields=("visit_price_brl", "contracted_price_brl"),
        transitions={
            "accept": Transition(frozenset({"draft"}), "held", event="services.contract.created"),
            "complete": Transition(frozenset({"held", "in_progress"}), "completed", event="services.contract.completed"),
            "dispute": Transition(frozenset({"held", "in_progress"}), "disputed", event="services.contract.disputed"),
        },
    ),
    ("mobility", "rides"): ResourceRule(
        ("origin", "destination", "vehicle_type"),
        initial_status="requested",
        protected_content=True,
        monetary_fields=("fare_brl",),
        transitions={
            "accept": Transition(frozenset({"requested"}), "accepted", event="mobility.ride.accepted"),
            "complete": Transition(frozenset({"accepted", "in_progress"}), "completed", event="mobility.ride.completed"),
            "cancel": Transition(frozenset({"requested", "accepted"}), "cancelled", event="mobility.ride.cancelled"),
        },
    ),
    ("mobility", "tickets"): ResourceRule(
        ("route_code", "amount_brl", "qr_token_hash"),
        ("qr_token_hash",),
        "active",
        monetary_fields=("amount_brl",),
        transitions={"use": Transition(frozenset({"active"}), "used", event="mobility.ticket.used")},
    ),
    ("jobs", "resumes"): ResourceRule(
        ("headline", "recruiter_visibility"),
        initial_status="active",
        sensitive=True,
    ),
    ("jobs", "employment_records"): ResourceRule(
        ("resume_id", "source_type", "employer_name", "started_on"),
        initial_status="active",
        sensitive=True,
    ),
    ("jobs", "resume_documents"): ResourceRule(
        ("resume_id", "document_type", "sha256", "evidence_status", "official_verification_status"),
        ("sha256",),
        "imported",
        immutable=True,
        sensitive=True,
    ),
    ("jobs", "job_postings"): ResourceRule(
        ("company_id", "company_status", "title", "description"),
        initial_status="draft",
        transitions={
            "publish": Transition(frozenset({"draft", "approved"}), "published", RECRUITER_ROLES, True, "jobs.job_posting.published"),
            "close": Transition(frozenset({"published"}), "closed", RECRUITER_ROLES, True, "jobs.job_posting.closed"),
        },
    ),
    ("jobs", "applications"): ResourceRule(
        ("job_posting_id", "resume_id"),
        initial_status="submitted",
        sensitive=True,
        transitions={
            "withdraw": Transition(frozenset({"submitted", "under_review"}), "withdrawn", event="jobs.application.withdrawn"),
            "review": Transition(frozenset({"submitted"}), "under_review", RECRUITER_ROLES, False, "jobs.application.reviewed"),
            "shortlist": Transition(frozenset({"submitted", "under_review"}), "shortlisted", RECRUITER_ROLES, True, "jobs.application.shortlisted"),
            "reject": Transition(frozenset({"submitted", "under_review", "shortlisted"}), "rejected", RECRUITER_ROLES, True, "jobs.application.rejected"),
        },
    ),
    ("jobs", "resume_access_logs"): ResourceRule(
        ("resume_id", "business_id", "purpose"),
        initial_status="recorded",
        immutable=True,
        sensitive=True,
    ),
    ("erp", "fiscal_documents"): ResourceRule(("document_type", "amount_brl"), monetary_fields=("amount_brl",), transitions=lifecycle_flow("erp.invoice")),
    ("wms", "warehouses"): ResourceRule(("name",), transitions=lifecycle_flow("wms.warehouse")),
    ("tms", "freights"): ResourceRule(("freight_brl",), monetary_fields=("freight_brl", "toll_brl"), transitions=lifecycle_flow("tms.freight")),
    ("crm", "opportunities"): ResourceRule(("title",), monetary_fields=("expected_value_brl",), transitions=lifecycle_flow("crm.opportunity")),
    ("bpm", "workflow_instances"): ResourceRule(("process_key",), initial_status="running", transitions=lifecycle_flow("bpm.workflow")),
    ("document", "documents"): ResourceRule(("storage_key", "filename"), sensitive=True, transitions=lifecycle_flow("document")),
    ("hr", "employees"): ResourceRule(("company_id", "employment_type"), sensitive=True, transitions=review_flow("hr.employee")),
    ("health", "patients"): ResourceRule(("health_identifier",), sensitive=True),
    ("health", "appointments"): ResourceRule(("patient_id", "professional_user_id", "scheduled_at"), sensitive=True, transitions=lifecycle_flow("health.appointment")),
    ("vision", "devices"): ResourceRule(("device_fingerprint",), sensitive=True, transitions=lifecycle_flow("vision.device")),
    ("legal", "cases"): ResourceRule(("case_number",), sensitive=True, monetary_fields=("risk_brl",), transitions=lifecycle_flow("legal.case")),
    ("property", "properties"): ResourceRule(("address", "property_type"), transitions=lifecycle_flow("property")),
    ("bi", "dashboards"): ResourceRule(("name", "definition"), transitions=lifecycle_flow("bi.dashboard")),
    ("ai_core", "moderation_decisions"): ResourceRule(("module", "risk_score"), sensitive=True, transitions=review_flow("ai.moderation")),
    ("api_hub", "api_clients"): ResourceRule(("client_name", "scopes"), sensitive=True, transitions=review_flow("api.client")),
}


def default_rule(module: str, resource_type: str) -> ResourceRule:
    return ResourceRule(transitions=lifecycle_flow(f"{module}.{resource_type.rstrip('s')}"))


def rule_for(module: str, resource_type: str) -> ResourceRule:
    if resource_type not in MODULE_ENTITIES.get(module, ()):
        raise HTTPException(status_code=404, detail=f"Recurso nao contratado para {module}: {resource_type}.")
    return RULE_OVERRIDES.get((module, resource_type), default_rule(module, resource_type))


def check_payload(rule: ResourceRule, payload: dict[str, Any]) -> None:
    missing = [field for field in rule.required_fields if payload.get(field) in (None, "")]
    if missing:
        raise HTTPException(status_code=422, detail=f"Campos obrigatorios ausentes: {', '.join(missing)}.")
    if rule.protected_content:
        material = str(payload)
        if any(pattern.search(material) for pattern in OFF_PLATFORM_PATTERNS):
            raise HTTPException(status_code=422, detail="Conteudo bloqueado pela politica anti-burla.")
    for field in rule.monetary_fields:
        value = payload.get(field)
        if value in (None, ""):
            continue
        try:
            if Decimal(str(value)) < 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            raise HTTPException(status_code=422, detail=f"Valor monetario invalido: {field}.") from None
    if "cpf_document" in payload and not CPF_DOCUMENT.fullmatch(str(payload["cpf_document"])):
        raise HTTPException(status_code=422, detail="Documento CPF/internacional invalido.")
    if "phone_e164" in payload and not PHONE_E164.fullmatch(str(payload["phone_e164"])):
        raise HTTPException(status_code=422, detail="Telefone deve usar formato E.164.")
    if payload.get("company_status") and payload["company_status"] not in {"approved", "active"}:
        raise HTTPException(status_code=422, detail="Operacao exige empresa aprovada.")
    if payload.get("recruiter_visibility") and payload["recruiter_visibility"] not in {"private", "business_recruiters"}:
        raise HTTPException(status_code=422, detail="Visibilidade de curriculo invalida.")


def event_for_create(module: str, resource_type: str) -> str:
    explicit = {
        ("identity", "users"): "identity.user.created",
        ("business", "companies"): "business.company.created",
        ("marketplace", "orders"): "marketplace.order.created",
        ("delivery", "delivery_requests"): "delivery.request.created",
        ("services", "service_contracts"): "services.contract.created",
        ("mobility", "rides"): "mobility.ride.requested",
        ("jobs", "resumes"): "jobs.resume.created",
        ("jobs", "employment_records"): "jobs.employment.self_declared",
        ("jobs", "job_postings"): "jobs.job_posting.created",
        ("jobs", "applications"): "jobs.application.created",
    }
    return explicit.get((module, resource_type), f"{module}.{resource_type.rstrip('s')}.created")


def can_read_sensitive(module: str, roles: frozenset[str]) -> bool:
    if module == "health":
        required = MEDICAL_ROLES
    elif module == "jobs":
        required = RECRUITER_ROLES
    else:
        required = SENSITIVE_ROLES
    return bool(roles & required)
