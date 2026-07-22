from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from modules.shared.business_postgres_store import BusinessPostgresStore
from modules.shared.identity_postgres_store import IdentityPostgresStore
from modules.shared.runtime import create_module_app


POSTGRES_DSN = os.environ.get(
    "ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN",
    "postgresql://all_in_one:local-development-only@localhost:5432/all_in_one?connect_timeout=3",
)


def _unique_phone_e164() -> str:
    return f"+55{uuid4().int % 10**11:011d}"


def _seed_identity_and_business(dsn: str) -> dict[str, str]:
    identity_store = IdentityPostgresStore(dsn=dsn)
    seed_user_id = str(uuid4())
    seed_user = identity_store.create(
        resource_type="users",
        user_id=seed_user_id,
        entity_id=None,
        status="active",
        payload={
            "id": seed_user_id,
            "full_name": f"Marketplace Seed {uuid4().hex[:6]}",
            "cpf_document": f"{uuid4().hex[:11]}",
            "birth_date": "1990-01-01",
            "email": f"marketplace_{uuid4().hex[:8]}@test.com",
            "phone_e164": _unique_phone_e164(),
            "password_hash": "seed-password-hash",
            "face_hash": f"seed-face-{uuid4().hex[:8]}",
            "liveness_score": 0.99,
            "terms_accepted_at": datetime.now(UTC).isoformat(),
            "lgpd_consent_at": datetime.now(UTC).isoformat(),
        },
        actor=seed_user_id,
        unique_fields=(),
        event="identity.user.created",
        idempotency_key=f"seed-user-{uuid4()}",
    )

    business_store = BusinessPostgresStore(dsn=dsn)
    seed_company = business_store.create(
        resource_type="companies",
        user_id=seed_user["id"],
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid4().hex[:14]}",
            "root_cnpj": f"{uuid4().hex[:14]}",
            "legal_name": f"Marketplace Seed {uuid4().hex[:6]} LTDA",
            "trade_name": f"Marketplace Seed {uuid4().hex[:6]}",
            "cnae": "6201500",
            "state_registration": "ISENTO",
            "municipal_registration": "ISENTO",
        },
        actor=seed_user["id"],
        unique_fields=(),
        event="business.company.created",
        idempotency_key=f"seed-company-{uuid4()}",
    )
    return {"user_id": seed_user["id"], "company_id": seed_company["id"]}


def _metrics_map(text: str, prefix: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith(prefix):
            continue
        key, value = line.split(" ", maxsplit=1)
        metrics[key] = value
    return metrics


def _create_marketplace_seed_data(store: Any, seeds: dict[str, str]) -> dict[str, str]:
    user_id = seeds["user_id"]
    company_id = seeds["company_id"]

    market_store = store.create(
        "stores",
        user_id,
        company_id,
        "active",
        {
            "company_id": company_id,
            "name": f"Loja Comercial {uuid4().hex[:6]}",
        },
        user_id,
        (),
        "marketplace.store.created",
        f"store-{uuid4()}",
    )

    paid_order = store.create(
        "orders",
        user_id,
        market_store["id"],
        "paid",
        {
            "store_id": market_store["id"],
            "company_id": company_id,
            "total_brl": "99.90",
            "commission_brl": "12.34",
            "offer_id": f"offer-{uuid4().hex[:8]}",
        },
        user_id,
        (),
        "marketplace.order.created",
        f"order-paid-{uuid4()}",
    )
    completed_order = store.create(
        "orders",
        user_id,
        market_store["id"],
        "completed",
        {
            "store_id": market_store["id"],
            "company_id": company_id,
            "total_brl": "149.90",
            "commission_brl": "18.90",
            "offer_id": f"offer-{uuid4().hex[:8]}",
        },
        user_id,
        (),
        "marketplace.order.created",
        f"order-completed-{uuid4()}",
    )
    store.create(
        "orders",
        user_id,
        market_store["id"],
        "created",
        {
            "store_id": market_store["id"],
            "company_id": company_id,
            "total_brl": "59.90",
            "commission_brl": "7.90",
            "offer_id": f"offer-{uuid4().hex[:8]}",
        },
        user_id,
        (),
        "marketplace.order.created",
        f"order-created-{uuid4()}",
    )
    store.create(
        "reviews",
        user_id,
        market_store["id"],
        "published",
        {
            "order_id": completed_order["id"],
            "store_id": market_store["id"],
            "offer_id": f"offer-{uuid4().hex[:8]}",
            "rating": 5,
            "comment": "Excelente atendimento.",
        },
        user_id,
        (),
        "valley.review.created",
        f"review-{uuid4()}",
    )
    store.create(
        "disputes",
        user_id,
        market_store["id"],
        "open",
        {
            "order_id": paid_order["id"],
            "store_id": market_store["id"],
            "company_id": company_id,
            "offer_id": f"offer-{uuid4().hex[:8]}",
            "case_type": "support",
            "subject": "Pedido em andamento",
            "message": "Preciso de uma atualizacao do pedido.",
            "desired_resolution": "Retorno do vendedor.",
        },
        user_id,
        (),
        "support.ticket.created",
        f"support-{uuid4()}",
    )
    store.create(
        "disputes",
        user_id,
        market_store["id"],
        "resolved",
        {
            "order_id": completed_order["id"],
            "store_id": market_store["id"],
            "company_id": company_id,
            "offer_id": f"offer-{uuid4().hex[:8]}",
            "case_type": "dispute",
            "subject": "Atraso resolvido",
            "message": "A disputa foi encerrada com acordo.",
            "desired_resolution": "Reembolso parcial.",
        },
        user_id,
        (),
        "marketplace.dispute.created",
        f"dispute-{uuid4()}",
    )

    return {
        "store_id": market_store["id"],
        "paid_order_id": paid_order["id"],
        "completed_order_id": completed_order["id"],
    }


def test_marketplace_metrics_expose_commercial_series(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN", POSTGRES_DSN)

    try:
        seeds = _seed_identity_and_business(POSTGRES_DSN)
        app = create_module_app("marketplace")
        store = app.extra["store"]
        _create_marketplace_seed_data(store, seeds)
    except Exception as exc:
        pytest.skip(f"Banco de dados nao disponivel para marketplace comercial: {exc}")

    client = TestClient(app)
    metrics_response = client.get("/metrics")
    insights_response = client.get("/valley/insights/commercial", headers={"X-Actor-User-Id": seeds["user_id"], "X-Actor-Roles": "auditor"})

    assert metrics_response.status_code == 200
    assert insights_response.status_code == 200

    metrics = _metrics_map(metrics_response.text, "all_in_one_marketplace_")
    assert metrics["all_in_one_marketplace_orders_total"] == "3"
    assert metrics["all_in_one_marketplace_orders_paid"] == "2"
    assert metrics["all_in_one_marketplace_orders_completed"] == "1"
    assert metrics["all_in_one_marketplace_reviews_total"] == "1"
    assert metrics["all_in_one_marketplace_support_cases_total"] == "2"
    assert metrics["all_in_one_marketplace_support_cases_open"] == "1"
    assert metrics["all_in_one_marketplace_support_cases_resolved"] == "1"
    assert metrics["all_in_one_marketplace_average_rating"] == "5.0"
    assert metrics["all_in_one_marketplace_conversion_rate_percent"] == "66.67"

    payload = insights_response.json()
    assert payload["orders_total"] == 3
    assert payload["orders_paid"] == 2
    assert payload["orders_completed"] == 1
    assert payload["reviews_total"] == 1
    assert payload["support_cases_total"] == 2
    assert payload["support_cases_open"] == 1
    assert payload["support_cases_resolved"] == 1
    assert payload["average_rating"] == 5.0
    assert payload["conversion_rate_percent"] == 66.67
