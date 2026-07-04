import hashlib

from modules.shared.integration_sandbox import (
    ApiHubSandbox,
    AiAgentSandbox,
    ClinicalConsentSandbox,
    CtpsSandbox,
    FiscalDocumentSandbox,
    IdentityVerificationSandbox,
    MapsRoutingSandbox,
    PspLedgerSandbox,
    SupplierCatalogSandbox,
    matrix_by_key,
    sandbox_adapters,
)


def test_all_matrix_sandbox_adapters_are_implemented() -> None:
    matrix = matrix_by_key()
    adapters = sandbox_adapters()

    assert set(matrix) == set(adapters)
    for key, adapter in adapters.items():
        assert getattr(adapter, "provider_key") == key
        assert getattr(adapter, "adapter") == matrix[key]["sandbox_adapter"]


def test_identity_verification_sandbox_hashes_sensitive_inputs() -> None:
    sandbox = IdentityVerificationSandbox()

    person = sandbox.verify_person(
        user_id="user-123",
        document="12345678901",
        full_name="Cliente Teste",
        selfie_hash="selfie-sha256",
    )
    business = sandbox.verify_business(
        company_id="company-123",
        cnpj="12345678000199",
        legal_name="Empresa Teste",
    )

    assert person.status == "approved"
    assert business.status == "approved"
    assert person.events[0]["routing_key"] == "identity.user.verified"
    assert business.events[0]["routing_key"] == "business.company.approved"
    assert person.payload["liveness_score"] == "0.99"
    assert "12345678901" not in str(person.payload)
    assert "Cliente Teste" not in str(person.payload)
    assert "12345678000199" not in str(business.payload)


def test_psp_fiscal_and_supplier_sandboxes_emit_domain_events() -> None:
    psp = PspLedgerSandbox()
    fiscal = FiscalDocumentSandbox()
    supplier = SupplierCatalogSandbox()

    pix = psp.authorize_pix("pay-1", "payer-1", "99.90", "idem-1")
    escrow = psp.create_escrow("escrow-1", "payer-1", "seller-1", "99.90")
    refund = psp.refund_payment("pay-1", "99.90", "refund-idem-1", "chargeback solicitado")
    invoice = fiscal.issue_invoice("invoice-1", "nfse", "99.90", "12345678000199")
    product = supplier.import_product("supplier-1", "SKU-123", "42.10", 10)

    assert pix.status == "authorized"
    assert pix.payload["amount_brl"] == "99.9000"
    assert escrow.status == "held"
    assert escrow.events[0]["routing_key"] == "payment.escrow.created"
    assert refund.status == "refunded"
    assert refund.events[0]["routing_key"] == "payment.refunded"
    assert "chargeback solicitado" not in str(refund.payload)
    assert invoice.status == "issued"
    assert invoice.events[0]["routing_key"] == "erp.invoice.created"
    assert "12345678000199" not in str(invoice.payload)
    assert product.status == "available"
    assert product.events[0]["routing_key"] == "stock.product.imported"


def test_maps_ctps_health_and_api_hub_sandboxes_are_deterministic() -> None:
    maps = MapsRoutingSandbox()
    ctps = CtpsSandbox()
    health = ClinicalConsentSandbox()
    api_hub = ApiHubSandbox()

    route = maps.route(
        "route-1",
        {"lat": -23.5505, "lng": -46.6333},
        {"lat": -23.5617, "lng": -46.6559},
        "motorcycle",
    )
    document = ctps.classify_pdf("resume-1", b"%PDF-1.4\nconteudo ctps")
    consent = health.record_consent("patient-1", "doctor-1", "teleconsulta")
    webhook = api_hub.sign_webhook("webhook-1", {"event": "delivery.completed"}, "sandbox-secret")
    api_key_hash = hashlib.sha256("dev-key".encode("utf-8")).hexdigest()
    api_key = api_hub.verify_api_key("dev-key", {api_key_hash})

    assert route.status == "calculated"
    assert float(route.payload["distance_km"]) > 0
    assert float(route.payload["eta_minutes"]) > 0
    assert document.status == "hash_preserved"
    assert document.events[0]["routing_key"] == "jobs.resume.ctps_imported"
    assert consent.status == "active"
    assert consent.payload["purpose"] == "teleconsulta"
    assert webhook.status == "signed"
    assert webhook.payload["signature_sha256"]
    assert "sandbox-secret" not in str(webhook.payload)
    assert api_key.status == "accepted"


def test_ai_agent_sandbox_emits_model_run_completed() -> None:
    sandbox = AiAgentSandbox()

    result = sandbox.run_prompt("run-1", "criar um layout de dashboard", module="ai_core")

    assert result.status == "completed"
    assert result.provider_key == "ai_agent_superdesign"
    assert result.events[0]["routing_key"] == "ai_core.model_run.completed"
    assert "criar um layout de dashboard" not in str(result.payload)
