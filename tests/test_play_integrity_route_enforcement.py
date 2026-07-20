from __future__ import annotations

from platform_test_support import fresh_client_for


class StubVerifier:
    def __init__(self, *, trusted: bool, rejection_type=None) -> None:
        self.trusted = trusted
        self.rejection_type = rejection_type
        self.calls: list[tuple[str | None, bytes]] = []

    def verify(self, token: str | None, body: bytes):
        self.calls.append((token, body))
        if not self.trusted:
            raise self.rejection_type("missing_token")
        return object()


def test_login_rejects_before_authentication_when_integrity_fails() -> None:
    client = fresh_client_for("identity")
    loaded_verifier = client.app.extra["play_integrity_verifier"]
    rejection_type = loaded_verifier.verify.__globals__["IntegrityRejected"]
    verifier = StubVerifier(trusted=False, rejection_type=rejection_type)
    client.app.extra["play_integrity_verifier"] = verifier

    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.test", "password": "invalid-password"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Integridade do aplicativo ou dispositivo rejeitada."
    )
    assert verifier.calls[0][0] is None
    assert b"invalid-password" in verifier.calls[0][1]


def test_login_route_forwards_opaque_token_and_exact_body_to_verifier() -> None:
    client = fresh_client_for("identity")
    verifier = StubVerifier(trusted=True)
    client.app.extra["play_integrity_verifier"] = verifier

    response = client.post(
        "/auth/login",
        headers={"X-Play-Integrity-Token": "opaque-google-token"},
        json={"email": "nobody@example.test", "password": "invalid-password"},
    )

    assert response.status_code == 401
    assert verifier.calls[0][0] == "opaque-google-token"
    assert verifier.calls[0][1].startswith(b"{")
