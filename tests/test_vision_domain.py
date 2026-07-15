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


def test_vision_stream_recording_and_motion_alert_journey() -> None:
    client = client_for("vision")
    actor = str(uuid4())
    nonce = uuid4().hex

    device = client.post(
        "/resources/devices",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "device_fingerprint": f"camera-{nonce}",
                "name": "Camera operacional",
            },
        },
    )
    assert device.status_code == 201

    stream = client.post(
        "/resources/streams",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "device_id": device.json()["id"],
                "stream_url_hash": "7" * 64,
                "protocol": "rtsp",
                "started_at": "2026-07-15T08:30:00Z",
            },
        },
    )
    assert stream.status_code == 201
    assert stream.json()["status"] == "active"
    assert "url" not in stream.json()["payload"]

    recording = client.post(
        "/resources/recordings",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "stream_id": stream.json()["id"],
                "storage_key": f"vault/vision/{nonce}/clip.mp4",
                "file_sha256": "8" * 64,
                "started_at": "2026-07-15T08:30:00Z",
            },
        },
    )
    assert recording.status_code == 201
    assert recording.json()["status"] == "recorded"

    motion_alert = client.post(
        "/resources/motion_alerts",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "device_id": device.json()["id"],
                "stream_id": stream.json()["id"],
                "detected_at": "2026-07-15T08:31:00Z",
                "confidence_score": "0.93",
            },
        },
    )
    assert motion_alert.status_code == 201
    assert motion_alert.json()["status"] == "detected"

    denied_triage = client.post(
        f"/resources/motion_alerts/{motion_alert.json()['id']}/actions/triage",
        headers=actor_headers(actor),
        json={"reason": "triagem sem MFA"},
    )
    assert denied_triage.status_code == 403

    triaged = client.post(
        f"/resources/motion_alerts/{motion_alert.json()['id']}/actions/triage",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "movimento relevante validado"},
    )
    assert triaged.status_code == 200
    assert triaged.json()["status"] == "under_review"

    resolved = client.post(
        f"/resources/motion_alerts/{motion_alert.json()['id']}/actions/resolve",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "incidente tratado"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"

    rejected_public_recording = client.post(
        "/resources/recordings",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "stream_id": stream.json()["id"],
                "storage_key": "https://public.example/clip.mp4",
                "file_sha256": "9" * 64,
                "started_at": "2026-07-15T08:30:00Z",
            },
        },
    )
    assert rejected_public_recording.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "vision.device.registered",
        "vision.stream.started",
        "vision.recording.stored",
        "vision.motion.detected",
        "vision.incident.created",
        "vision.incident.resolved",
    } <= routing_keys
