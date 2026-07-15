from __future__ import annotations

from uuid import uuid4

from platform_test_support import client_for


def actor_headers(user_id: str, roles: str = "administrator") -> dict[str, str]:
    return {"X-Actor-User-Id": user_id, "X-Actor-Roles": roles}


def document_payload(nonce: str) -> dict[str, str]:
    return {
        "storage_provider": "private_vault",
        "storage_bucket": "all-in-one-private-documents",
        "storage_key": f"vault/document/{nonce}/contract.pdf",
        "file_sha256": "f" * 64,
        "kms_key_version": "kms://document/private-vault/v1",
        "filename": "contract.pdf",
        "content_type": "application/pdf",
    }


def version_payload(document_id: str, nonce: str, version: str = "2") -> dict[str, str]:
    return {
        "document_id": document_id,
        "version": version,
        "storage_key": f"vault/document/{nonce}/contract-v{version}.pdf",
        "file_sha256": "a" * 64,
        "kms_key_version": "kms://document/private-vault/v2",
    }


def test_document_upload_and_version_use_private_storage_contract() -> None:
    client = client_for("document")
    actor = str(uuid4())
    nonce = uuid4().hex

    uploaded = client.post(
        "/resources/documents",
        headers=actor_headers(actor),
        json={"user_id": actor, "payload": document_payload(nonce)},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["status"] == "draft"
    assert uploaded.json()["payload"]["storage_provider"] == "private_vault"
    assert uploaded.json()["payload"]["kms_key_version"].endswith("/v1")

    versioned = client.post(
        "/resources/versions",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": version_payload(uploaded.json()["id"], nonce),
        },
    )
    assert versioned.status_code == 201
    assert versioned.json()["payload"]["document_id"] == uploaded.json()["id"]
    assert versioned.json()["payload"]["version"] == "2"

    rejected_public_storage = client.post(
        "/resources/documents",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                **document_payload(nonce),
                "storage_key": "https://public.example/document.pdf",
            },
        },
    )
    assert rejected_public_storage.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {"document.uploaded", "document.versioned"} <= routing_keys
