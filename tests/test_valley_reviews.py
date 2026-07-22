from uuid import uuid4

from platform_test_support import fresh_client_for


def actor_headers(user_id: str, *, roles: str = "") -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": roles,
    }


def approver_headers(user_id: str) -> dict[str, str]:
    return {
        **actor_headers(user_id, roles="administrator"),
        "X-MFA-Verified": "true",
    }


def test_marketplace_review_is_immutable_and_emits_valley_event() -> None:
    marketplace = fresh_client_for("marketplace")
    user_id = str(uuid4())
    order_id = str(uuid4())

    created = marketplace.post(
        "/resources/reviews",
        headers={
            **actor_headers(user_id),
            "X-Idempotency-Key": f"review-{order_id}",
        },
        json={
            "user_id": user_id,
            "payload": {
                "order_id": order_id,
                "rating": 5,
                "comment": "Atendimento concluido conforme combinado.",
            },
        },
    )

    assert created.status_code == 201
    assert created.json()["status"] == "pending_review"
    assert created.json()["payload"]["moderation_status"] == "pending_review"

    patch = marketplace.patch(
        f"/resources/reviews/{created.json()['id']}",
        headers=actor_headers(user_id),
        json={"payload": {"rating": 1}},
    )
    assert patch.status_code == 409

    insights_before = marketplace.get(
        "/valley/insights/commercial",
        headers=actor_headers(user_id),
    )
    assert insights_before.status_code == 200
    assert insights_before.json()["reviews_pending_moderation"] == 1
    assert insights_before.json()["reviews_published"] == 0
    assert insights_before.json()["average_rating"] is None

    published = marketplace.post(
        f"/resources/reviews/{created.json()['id']}/actions/publish",
        headers=approver_headers(str(uuid4())),
        json={
            "reason": "avaliacao conferida sem contato externo",
            "payload": {"moderation_status": "published"},
        },
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    outbox = marketplace.get(
        "/events/outbox",
        headers=actor_headers(user_id, roles="auditor"),
    )
    assert outbox.status_code == 200
    assert any(
        event["routing_key"] == "valley.review.created" for event in outbox.json()
    )
    assert any(
        event["routing_key"] == "valley.review.published" for event in outbox.json()
    )

    insights_after = marketplace.get(
        "/valley/insights/commercial",
        headers=actor_headers(user_id),
    )
    assert insights_after.status_code == 200
    assert insights_after.json()["reviews_pending_moderation"] == 0
    assert insights_after.json()["reviews_published"] == 1
    assert insights_after.json()["average_rating"] == 5.0


def test_marketplace_review_applies_basic_off_platform_moderation() -> None:
    marketplace = fresh_client_for("marketplace")
    user_id = str(uuid4())

    response = marketplace.post(
        "/resources/reviews",
        headers=actor_headers(user_id),
        json={
            "user_id": user_id,
            "payload": {
                "order_id": str(uuid4()),
                "rating": 3,
                "comment": "Fale comigo pelo WhatsApp.",
            },
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Conteudo bloqueado pela politica anti-burla."
