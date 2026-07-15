from __future__ import annotations

from uuid import uuid4

from platform_test_support import client_for


def actor_headers(
    user_id: str,
    roles: str = "administrator",
    *,
    mfa_verified: bool = False,
) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": roles,
        "X-MFA-Verified": "true" if mfa_verified else "false",
    }


def test_erp_payables_receivables_and_reconciliation_journey() -> None:
    client = client_for("erp")
    actor = str(uuid4())
    nonce = uuid4().hex

    account = client.post(
        "/resources/accounts",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "account_code": f"CAIXA-{nonce}",
                "name": "Conta operacional",
            },
        },
    )
    assert account.status_code == 201
    assert account.json()["status"] == "active"

    cost_center = client.post(
        "/resources/cost_centers",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "cost_center_code": f"CC-{nonce}",
                "name": "Operacao fiscal",
            },
        },
    )
    assert cost_center.status_code == 201
    assert cost_center.json()["status"] == "active"

    payable = client.post(
        "/resources/payables",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "supplier_name": "Fornecedor auditavel",
                "due_at": "2026-08-05",
                "amount_brl": "890.50",
                "cost_center_id": cost_center.json()["id"],
            },
        },
    )
    assert payable.status_code == 201
    assert payable.json()["status"] == "open"

    denied_payment = client.post(
        f"/resources/payables/{payable.json()['id']}/actions/approve_payment",
        headers=actor_headers(actor),
        json={"reason": "pagamento sem MFA"},
    )
    assert denied_payment.status_code == 403

    approved_payment = client.post(
        f"/resources/payables/{payable.json()['id']}/actions/approve_payment",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "nota fiscal validada"},
    )
    assert approved_payment.status_code == 200
    assert approved_payment.json()["status"] == "approved"

    paid = client.post(
        f"/resources/payables/{payable.json()['id']}/actions/settle",
        headers=actor_headers(actor),
        json={"reason": "pagamento baixado no sandbox"},
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"

    receivable = client.post(
        "/resources/receivables",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "customer_name": "Cliente auditavel",
                "due_at": "2026-08-10",
                "amount_brl": "1290.75",
                "account_id": account.json()["id"],
            },
        },
    )
    assert receivable.status_code == 201
    assert receivable.json()["status"] == "issued"

    received = client.post(
        f"/resources/receivables/{receivable.json()['id']}/actions/receive",
        headers=actor_headers(actor),
        json={"reason": "recebimento identificado no extrato sandbox"},
    )
    assert received.status_code == 200
    assert received.json()["status"] == "received"

    denied_reconciliation = client.post(
        f"/resources/receivables/{receivable.json()['id']}/actions/reconcile",
        headers=actor_headers(actor),
        json={"reason": "conciliacao sem MFA"},
    )
    assert denied_reconciliation.status_code == 403

    reconciled = client.post(
        f"/resources/receivables/{receivable.json()['id']}/actions/reconcile",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "extrato conciliado com titulo"},
    )
    assert reconciled.status_code == 200
    assert reconciled.json()["status"] == "reconciled"

    rejected_negative_payable = client.post(
        "/resources/payables",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "supplier_name": "Fornecedor invalido",
                "due_at": "2026-08-05",
                "amount_brl": "-1.00",
                "cost_center_id": cost_center.json()["id"],
            },
        },
    )
    assert rejected_negative_payable.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "erp.account.created",
        "erp.cost_center.created",
        "erp.payable.created",
        "erp.payment.approved",
        "erp.payable.paid",
        "erp.receivable.created",
        "erp.receivable.received",
        "erp.receivable.reconciled",
    } <= routing_keys
