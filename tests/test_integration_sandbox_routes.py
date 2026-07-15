import hashlib
from uuid import uuid4

from platform_test_support import fresh_client_for


def sandbox_headers() -> dict[str, str]:
    return {
        "X-Actor-User-Id": str(uuid4()),
        "X-Actor-Roles": "compliance_officer",
        "X-MFA-Verified": "true",
    }


def test_identity_business_finance_sandbox_routes() -> None:
    identity = fresh_client_for("identity")
    business = fresh_client_for("business")
    finance = fresh_client_for("finance")

    denied = identity.post(
        "/integrations/sandbox/kyc/person",
        headers={"X-Actor-User-Id": str(uuid4())},
        json={"user_id": "user-1", "document": "12345678901", "full_name": "Cliente Teste"},
    )
    assert denied.status_code == 403

    kyc = identity.post(
        "/integrations/sandbox/kyc/person",
        headers=sandbox_headers(),
        json={"user_id": "user-1", "document": "12345678901", "full_name": "Cliente Teste"},
    )
    assert kyc.status_code == 200
    assert kyc.json()["provider_key"] == "identity_kyc_kyb"
    assert kyc.json()["status"] == "approved"
    assert kyc.json()["audit"]["audit_id"].startswith("sandbox_audit_")
    assert kyc.json()["audit"]["provider_environment"] == "sandbox"
    assert kyc.json()["audit"]["event_routing_keys"] == ["identity.user.verified"]
    assert "12345678901" not in str(kyc.json()["payload"])
    assert "12345678901" not in str(kyc.json()["audit"])

    kyb = business.post(
        "/integrations/sandbox/kyb/business",
        headers=sandbox_headers(),
        json={"company_id": "company-1", "cnpj": "12345678000199", "legal_name": "Empresa Teste"},
    )
    assert kyb.status_code == 200
    assert kyb.json()["events"][0]["routing_key"] == "business.company.approved"

    pix = finance.post(
        "/integrations/sandbox/psp/pix/authorize",
        headers=sandbox_headers(),
        json={"payment_id": "pay-1", "payer_id": "payer-1", "amount_brl": "99.90", "idempotency_key": "idem-1"},
    )
    assert pix.status_code == 200
    assert pix.json()["status"] == "authorized"
    assert pix.json()["audit"]["payload_sha256"]

    escrow = finance.post(
        "/integrations/sandbox/psp/escrows",
        headers=sandbox_headers(),
        json={"escrow_id": "escrow-1", "payer_id": "payer-1", "beneficiary_id": "seller-1", "amount_brl": "99.90"},
    )
    assert escrow.status_code == 200
    assert escrow.json()["events"][0]["routing_key"] == "payment.escrow.created"


def test_logistics_jobs_health_api_hub_and_supplier_sandbox_routes() -> None:
    delivery = fresh_client_for("delivery")
    jobs = fresh_client_for("jobs")
    health = fresh_client_for("health")
    api_hub = fresh_client_for("api_hub")
    stock = fresh_client_for("stock")
    erp = fresh_client_for("erp")

    route = delivery.post(
        "/integrations/sandbox/maps/route",
        headers=sandbox_headers(),
        json={
            "route_id": "route-1",
            "origin": {"lat": -23.5505, "lng": -46.6333},
            "destination": {"lat": -23.5617, "lng": -46.6559},
            "vehicle_type": "motorcycle",
        },
    )
    assert route.status_code == 200
    assert route.json()["provider_key"] == "maps_routing_tracking"
    assert float(route.json()["payload"]["distance_km"]) > 0

    ctps = jobs.post(
        "/integrations/sandbox/ctps/classify",
        headers=sandbox_headers(),
        json={"resume_id": "resume-1", "pdf_text": "%PDF-1.4 ctps"},
    )
    assert ctps.status_code == 200
    assert ctps.json()["status"] == "hash_preserved"

    consent = health.post(
        "/integrations/sandbox/health/consents",
        headers=sandbox_headers(),
        json={"patient_id": "patient-1", "professional_id": "doctor-1", "purpose": "teleconsulta"},
    )
    assert consent.status_code == 200
    assert consent.json()["status"] == "active"

    webhook = api_hub.post(
        "/integrations/sandbox/api-hub/webhooks/sign",
        headers=sandbox_headers(),
        json={"webhook_id": "webhook-1", "payload": {"event": "delivery.completed"}, "secret": "sandbox-secret"},
    )
    assert webhook.status_code == 200
    assert webhook.json()["status"] == "signed"
    assert "sandbox-secret" not in str(webhook.json()["payload"])

    api_key_hash = hashlib.sha256("dev-key".encode("utf-8")).hexdigest()
    api_key = api_hub.post(
        "/integrations/sandbox/api-hub/api-key/verify",
        headers=sandbox_headers(),
        json={"api_key": "dev-key", "allowed_hashes": [api_key_hash]},
    )
    assert api_key.status_code == 200
    assert api_key.json()["status"] == "accepted"

    product = stock.post(
        "/integrations/sandbox/suppliers/products",
        headers=sandbox_headers(),
        json={"supplier_id": "supplier-1", "external_sku": "SKU-1", "cost_brl": "42.10", "available_quantity": 5},
    )
    assert product.status_code == 200
    assert product.json()["events"][0]["routing_key"] == "stock.product.imported"

    invoice = erp.post(
        "/integrations/sandbox/fiscal/invoices",
        headers=sandbox_headers(),
        json={"invoice_id": "invoice-1", "document_type": "nfse", "amount_brl": "99.90", "issuer_document": "12345678000199"},
    )
    assert invoice.status_code == 200
    assert invoice.json()["events"][0]["routing_key"] == "erp.invoice.created"
    assert invoice.json()["audit"]["event_routing_keys"] == ["erp.invoice.created"]
