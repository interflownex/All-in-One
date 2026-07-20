from __future__ import annotations

import base64
import hashlib

import pytest

from modules.identity.play_integrity import IntegrityRejected, PlayIntegrityVerifier

PACKAGE = "com.example.valley"
CERTIFICATE = "ab" * 32
NOW_MS = 1_800_000_000_000
BODY = b'{"email":"user@example.test","password":"secret"}'


def _hash(body: bytes) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(body).digest()).decode().rstrip("=")


def _certificate_b64() -> str:
    return base64.urlsafe_b64encode(bytes.fromhex(CERTIFICATE)).decode().rstrip("=")


def _verdict(**overrides):
    verdict = {
        "tokenPayloadExternal": {
            "requestDetails": {
                "requestPackageName": PACKAGE,
                "requestHash": _hash(BODY),
                "timestampMillis": str(NOW_MS - 1_000),
            },
            "appIntegrity": {
                "appRecognitionVerdict": "PLAY_RECOGNIZED",
                "packageName": PACKAGE,
                "certificateSha256Digest": [_certificate_b64()],
            },
            "deviceIntegrity": {"deviceRecognitionVerdict": ["MEETS_DEVICE_INTEGRITY"]},
            "accountDetails": {"appLicensingVerdict": "LICENSED"},
            "environmentDetails": {
                "appAccessRiskVerdict": {"appsDetected": ["KNOWN_INSTALLED"]}
            },
        }
    }
    verdict["tokenPayloadExternal"].update(overrides)
    return verdict


def _verifier(payload, *, enforce=True):
    return PlayIntegrityVerifier(
        package_name=PACKAGE,
        certificate_sha256=CERTIFICATE,
        enforce=enforce,
        decoder=lambda _package, _token: payload,
        now_ms=lambda: NOW_MS,
    )


def test_valid_verdict_is_bound_to_raw_request_and_release_certificate() -> None:
    decision = _verifier(_verdict()).verify("opaque-token", BODY)

    assert decision.trusted is True
    assert decision.reason == "trusted"
    assert decision.device_labels == ("MEETS_DEVICE_INTEGRITY",)


@pytest.mark.parametrize(
    ("payload", "body", "reason"),
    [
        (_verdict(), b'{"tampered":true}', "request_hash"),
        (
            _verdict(
                requestDetails={
                    "requestPackageName": "evil.app",
                    "requestHash": _hash(BODY),
                    "timestampMillis": str(NOW_MS),
                }
            ),
            BODY,
            "package_name",
        ),
        (
            _verdict(
                requestDetails={
                    "requestPackageName": PACKAGE,
                    "requestHash": _hash(BODY),
                    "timestampMillis": str(NOW_MS - 500_000),
                }
            ),
            BODY,
            "stale_token",
        ),
        (
            _verdict(
                appIntegrity={
                    "appRecognitionVerdict": "UNRECOGNIZED_VERSION",
                    "certificateSha256Digest": [_certificate_b64()],
                }
            ),
            BODY,
            "app_recognition",
        ),
        (
            _verdict(
                deviceIntegrity={"deviceRecognitionVerdict": ["MEETS_BASIC_INTEGRITY"]}
            ),
            BODY,
            "device_integrity",
        ),
        (
            _verdict(
                environmentDetails={
                    "appAccessRiskVerdict": {"appsDetected": ["UNKNOWN_CONTROLLING"]}
                }
            ),
            BODY,
            "app_access_risk",
        ),
    ],
)
def test_untrusted_verdicts_are_rejected(payload, body: bytes, reason: str) -> None:
    with pytest.raises(IntegrityRejected, match=reason):
        _verifier(payload).verify("opaque-token", body)


def test_missing_token_is_fail_closed_only_when_enforced() -> None:
    with pytest.raises(IntegrityRejected, match="missing_token"):
        _verifier(_verdict(), enforce=True).verify(None, BODY)

    decision = _verifier(_verdict(), enforce=False).verify(None, BODY)
    assert decision.reason == "development_bypass"
    assert decision.trusted is False
