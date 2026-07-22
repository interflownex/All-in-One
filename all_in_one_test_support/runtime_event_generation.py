from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from modules.shared.domain_rules import ResourceRule


ROOT = Path(__file__).resolve().parents[1]


def load_module_catalog() -> dict:
    return json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))


def get_primary_resource(module_slug: str) -> str | None:
    catalog = load_module_catalog()
    for module in catalog["modules"]:
        if module["slug"] == module_slug:
            if not module["entities"]:
                return None
            return module["entities"][0]
    raise ValueError(f"Module {module_slug} not found in catalog")


def sample_geo_point() -> dict[str, float]:
    return {"latitude": -23.5505, "longitude": -46.6333}


def resolve_entity_id(payload: dict[str, object]) -> str | None:
    for key in ("company_id", "business_id", "store_id", "wallet_id", "resume_id"):
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def generate_payload(rule: ResourceRule, user_id: str) -> dict[str, object]:
    payload: dict[str, object] = {"user_id": user_id}
    for field in rule.required_fields:
        if field in payload:
            continue
        if field == "company_status":
            payload[field] = "active"
        elif field == "recruiter_visibility":
            payload[field] = "business_recruiters"
        elif field == "wallet_type":
            payload[field] = "personal"
        elif field == "service_type":
            payload[field] = "package"
        elif field == "vehicle_type":
            payload[field] = "car"
        elif field == "category":
            payload[field] = "maintenance"
        elif field == "employment_type":
            payload[field] = "full_time"
        elif field == "origin" or field == "destination":
            payload[field] = sample_geo_point()
        elif field == "scopes":
            payload[field] = ["orders:read"]
        elif field == "definition":
            payload[field] = {"widgets": []}
        elif field == "address":
            payload[field] = {
                "street": "Rua Exemplo",
                "city": "Sao Paulo",
                "state": "SP",
                "zip_code": "01000-000",
            }
        elif field == "risk_score":
            payload[field] = 0.42
        elif field == "health_identifier":
            payload[field] = f"health-{uuid4().hex[:8]}"
        elif field == "device_fingerprint":
            payload[field] = f"device-{uuid4().hex[:8]}"
        elif field == "case_number":
            payload[field] = f"CASE-{uuid4().hex[:10].upper()}"
        elif field == "client_name":
            payload[field] = "Integration Client"
        elif field == "client_id_hash":
            payload[field] = uuid4().hex
        elif field == "secret_reference":
            payload[field] = f"secret-{uuid4().hex[:8]}"
        elif field == "cnpj":
            payload[field] = "12345678000195"
        elif field == "root_cnpj":
            payload[field] = "12345678"
        elif field == "headline":
            payload[field] = "Test Headline"
        elif field == "title":
            payload[field] = "Test Title"
        elif field == "content":
            payload[field] = "Test Content"
        elif field == "description":
            payload[field] = "Test Description"
        elif field == "message":
            payload[field] = "Test Message"
        elif field == "name":
            payload[field] = "Test Name"
        elif "document_cnpj" in field:
            payload[field] = "12345678000195"
        elif "document" in field:
            payload[field] = "123456789"
        elif "hash" in field:
            payload[field] = uuid4().hex
        elif "amount" in field:
            payload[field] = "100.00"
        elif "price" in field:
            payload[field] = "100.00"
        elif "total" in field:
            payload[field] = "100.00"
        elif "id" in field:
            payload[field] = str(uuid4())
        else:
            payload[field] = "default"
    return payload


def get_evented_transition(rule: ResourceRule) -> tuple[str, object] | None:
    for name, transition in rule.transitions.items():
        if transition.event and rule.initial_status in transition.source:
            return name, transition
    return None
