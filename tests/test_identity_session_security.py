from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import jwt

from modules.identity.auth_logic import (
    JWT_ALGORITHM,
    JWT_SECRET,
    totp_code,
    totp_counter,
)
from platform_test_support import fresh_client_for


def _registered_user(client):
    nonce = uuid4().hex
    password = "Valley-Session-Password-2026!"
    response = client.post(
        "/registrations",
        json={
            "full_name": "Usuario Valley Sessao",
            "cpf_document": f"CPF-{nonce[:12]}",
            "email": f"session-{nonce}@example.test",
            "phone_e164": f"+55{str(int(nonce[:8], 16)).zfill(10)[-10:]}",
            "password_hash": password,
            "face_hash": f"face-{nonce}",
            "terms_accepted_at": "2026-07-19T22:00:00Z",
            "lgpd_consent_at": "2026-07-19T22:00:00Z",
        },
    )
    assert response.status_code == 201, response.text
    user = response.json()
    assert "password_hash" not in user["payload"]
    return user, password


def test_login_creates_hashed_server_session_and_short_lived_access_token() -> None:
    client = fresh_client_for("identity")
    user, password = _registered_user(client)
    fingerprint = "valley-test-device-001"

    login = client.post(
        "/auth/login",
        headers={"X-Device-Fingerprint": fingerprint},
        json={"email": user["payload"]["email"], "password": password},
    )

    assert login.status_code == 200, login.text
    payload = login.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["session_id"]
    access_expires_at = datetime.fromisoformat(payload["expires_at"])
    assert (
        0 < (access_expires_at - datetime.now(UTC)).total_seconds() <= 16 * 60
    )
    sessions = client.get(
        "/resources/sessions",
        headers={"X-Actor-User-Id": user["id"]},
    )
    assert sessions.status_code == 200
    stored = sessions.json()[0]
    assert stored["status"] == "active"
    assert stored["payload"]["device_fingerprint"] == fingerprint
    assert stored["payload"]["token_hash"] != payload["refresh_token"]


def test_refresh_rotates_token_rejects_replay_and_logout_revokes_session() -> None:
    client = fresh_client_for("identity")
    user, password = _registered_user(client)
    fingerprint = "valley-test-device-rotation"
    login = client.post(
        "/auth/login",
        headers={"X-Device-Fingerprint": fingerprint},
        json={"email": user["payload"]["email"], "password": password},
    ).json()

    rotated = client.post(
        "/auth/refresh",
        json={
            "refresh_token": login["refresh_token"],
            "device_fingerprint": fingerprint,
        },
    )
    assert rotated.status_code == 200, rotated.text
    assert rotated.json()["refresh_token"] != login["refresh_token"]

    replay = client.post(
        "/auth/refresh",
        json={
            "refresh_token": login["refresh_token"],
            "device_fingerprint": fingerprint,
        },
    )
    assert replay.status_code == 401

    logout = client.post(
        "/auth/logout",
        json={
            "refresh_token": rotated.json()["refresh_token"],
            "device_fingerprint": fingerprint,
        },
    )
    assert logout.status_code == 200
    after_logout = client.post(
        "/auth/refresh",
        json={
            "refresh_token": rotated.json()["refresh_token"],
            "device_fingerprint": fingerprint,
        },
    )
    assert after_logout.status_code == 401


def test_refresh_revokes_session_when_device_fingerprint_changes() -> None:
    client = fresh_client_for("identity")
    user, password = _registered_user(client)
    login = client.post(
        "/auth/login",
        headers={"X-Device-Fingerprint": "valley-original-device"},
        json={"email": user["payload"]["email"], "password": password},
    ).json()

    mismatch = client.post(
        "/auth/refresh",
        json={
            "refresh_token": login["refresh_token"],
            "device_fingerprint": "valley-other-device",
        },
    )
    assert mismatch.status_code == 401
    assert "Dispositivo" in mismatch.json()["detail"]


def _actor_headers(user_id: str) -> dict[str, str]:
    return {"X-Actor-User-Id": user_id, "X-Actor-Roles": "consumer"}


def test_totp_setup_encrypts_secret_verifies_real_code_and_rejects_replay() -> None:
    client = fresh_client_for("identity")
    user, password = _registered_user(client)
    login = client.post(
        "/auth/login",
        headers={"X-Device-Fingerprint": "valley-mfa-device"},
        json={"email": user["payload"]["email"], "password": password},
    ).json()
    setup = client.post(
        "/mfa/setup",
        headers=_actor_headers(user["id"]),
        json={"user_id": user["id"], "method": "totp"},
    )
    assert setup.status_code == 200, setup.text
    enrollment = setup.json()
    assert enrollment["secret"] != "JBSWY3DPEHPK3PXP"
    factors = client.get(
        "/resources/identity_verifications", headers=_actor_headers(user["id"])
    )
    stored = factors.json()[0]
    assert enrollment["secret"] not in str(stored["payload"])
    assert stored["payload"]["secret_ciphertext"]

    code = totp_code(enrollment["secret"], totp_counter())
    verified = client.post(
        "/mfa/verify",
        headers=_actor_headers(user["id"]),
        json={
            "user_id": user["id"],
            "session_id": login["session_id"],
            "method": "totp",
            "code": code,
        },
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["status"] == "verified"
    assert verified.json()["access_token"]
    claims = jwt.decode(
        verified.json()["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    assert claims["mfa_verified"] is True
    assert claims["sid"] == login["session_id"]

    replay = client.post(
        "/mfa/verify",
        headers=_actor_headers(user["id"]),
        json={
            "user_id": user["id"],
            "session_id": login["session_id"],
            "method": "totp",
            "code": code,
        },
    )
    assert replay.status_code == 401
    assert "reutilizado" in replay.json()["detail"]


def test_mfa_rejects_cross_account_enrollment_and_fake_sms_delivery() -> None:
    client = fresh_client_for("identity")
    owner, _ = _registered_user(client)
    other, _ = _registered_user(client)
    forbidden = client.post(
        "/mfa/setup",
        headers=_actor_headers(owner["id"]),
        json={"user_id": other["id"], "method": "totp"},
    )
    assert forbidden.status_code == 403

    unsupported = client.post(
        "/mfa/setup",
        headers=_actor_headers(owner["id"]),
        json={"user_id": owner["id"], "method": "sms"},
    )
    assert unsupported.status_code == 501
