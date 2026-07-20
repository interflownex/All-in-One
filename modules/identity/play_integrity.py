from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

PLAY_INTEGRITY_SCOPE = "https://www.googleapis.com/auth/playintegrity"


class IntegrityConfigurationError(RuntimeError):
    pass


class IntegrityRejected(ValueError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class IntegrityDecision:
    trusted: bool
    reason: str
    device_labels: tuple[str, ...] = ()


DecodeToken = Callable[[str, str], dict[str, Any]]


class PlayIntegrityVerifier:
    def __init__(
        self,
        *,
        package_name: str | None = None,
        certificate_sha256: str | None = None,
        enforce: bool | None = None,
        max_age_seconds: int | None = None,
        decoder: DecodeToken | None = None,
        now_ms: Callable[[], int] | None = None,
    ) -> None:
        environment = os.getenv("ALL_IN_ONE_ENV", "development").casefold()
        self.package_name = package_name or os.getenv(
            "VALLEY_ANDROID_PACKAGE_NAME", "com.example.valley"
        )
        self.certificate_sha256 = _normalize_hex(
            certificate_sha256 or os.getenv("VALLEY_PLAY_APP_SIGNING_CERT_SHA256", "")
        )
        self.enforce = environment == "production" if enforce is None else enforce
        self.max_age_seconds = max_age_seconds or int(
            os.getenv("VALLEY_PLAY_INTEGRITY_MAX_AGE_SECONDS", "120")
        )
        self.decoder = decoder or self._decode_with_google
        self.now_ms = now_ms or (lambda: int(time.time() * 1000))

    def verify(
        self, integrity_token: str | None, request_body: bytes
    ) -> IntegrityDecision:
        if not integrity_token:
            if self.enforce:
                raise IntegrityRejected("missing_token")
            return IntegrityDecision(trusted=False, reason="development_bypass")
        self._validate_configuration()
        payload = self.decoder(self.package_name, integrity_token)
        verdict = payload.get("tokenPayloadExternal", payload)
        self._validate_request_details(verdict.get("requestDetails", {}), request_body)
        self._validate_app_integrity(verdict.get("appIntegrity", {}))
        device_labels = tuple(
            verdict.get("deviceIntegrity", {}).get("deviceRecognitionVerdict", ())
        )
        if "MEETS_DEVICE_INTEGRITY" not in device_labels:
            raise IntegrityRejected("device_integrity")
        licensing = verdict.get("accountDetails", {}).get("appLicensingVerdict")
        if licensing not in {None, "LICENSED"}:
            raise IntegrityRejected("app_licensing")
        apps_detected = set(
            verdict.get("environmentDetails", {})
            .get("appAccessRiskVerdict", {})
            .get("appsDetected", ())
        )
        if apps_detected & {"UNKNOWN_CAPTURING", "UNKNOWN_CONTROLLING"}:
            raise IntegrityRejected("app_access_risk")
        return IntegrityDecision(
            trusted=True, reason="trusted", device_labels=device_labels
        )

    def _validate_configuration(self) -> None:
        if len(self.certificate_sha256) != 64:
            raise IntegrityConfigurationError(
                "VALLEY_PLAY_APP_SIGNING_CERT_SHA256 invalido ou ausente."
            )
        if not 30 <= self.max_age_seconds <= 300:
            raise IntegrityConfigurationError(
                "VALLEY_PLAY_INTEGRITY_MAX_AGE_SECONDS deve ficar entre 30 e 300."
            )

    def _validate_request_details(
        self, details: dict[str, Any], request_body: bytes
    ) -> None:
        expected_hash = _request_hash(request_body)
        if not hmac.compare_digest(
            str(details.get("requestPackageName", "")), self.package_name
        ):
            raise IntegrityRejected("package_name")
        if not hmac.compare_digest(str(details.get("requestHash", "")), expected_hash):
            raise IntegrityRejected("request_hash")
        try:
            timestamp_ms = int(details["timestampMillis"])
        except (KeyError, TypeError, ValueError) as exc:
            raise IntegrityRejected("timestamp") from exc
        age_ms = self.now_ms() - timestamp_ms
        if age_ms < -10_000 or age_ms > self.max_age_seconds * 1000:
            raise IntegrityRejected("stale_token")

    def _validate_app_integrity(self, app_integrity: dict[str, Any]) -> None:
        if app_integrity.get("appRecognitionVerdict") != "PLAY_RECOGNIZED":
            raise IntegrityRejected("app_recognition")
        if app_integrity.get("packageName") not in {None, self.package_name}:
            raise IntegrityRejected("app_package")
        certificates = {
            normalized
            for value in app_integrity.get("certificateSha256Digest", ())
            if (normalized := _certificate_digest_to_hex(str(value)))
        }
        if self.certificate_sha256 not in certificates:
            raise IntegrityRejected("app_certificate")

    @staticmethod
    def _decode_with_google(package_name: str, integrity_token: str) -> dict[str, Any]:
        try:
            import google.auth
            from google.auth.transport.requests import AuthorizedSession
        except ModuleNotFoundError as exc:
            raise IntegrityConfigurationError(
                "google-auth obrigatorio para validar Play Integrity."
            ) from exc
        try:
            credentials, _ = google.auth.default(scopes=[PLAY_INTEGRITY_SCOPE])
            session = AuthorizedSession(credentials)
            response = session.post(
                f"https://playintegrity.googleapis.com/v1/{package_name}:decodeIntegrityToken",
                json={"integrity_token": integrity_token},
                timeout=10,
            )
        except Exception as exc:
            raise IntegrityConfigurationError(
                "Nao foi possivel consultar a Play Integrity API."
            ) from exc
        if response.status_code >= 500:
            raise IntegrityConfigurationError("Play Integrity API indisponivel.")
        if response.status_code != 200:
            raise IntegrityRejected("decode_token")
        try:
            return dict(response.json())
        except (TypeError, ValueError) as exc:
            raise IntegrityConfigurationError(
                "Resposta Play Integrity invalida."
            ) from exc


def _request_hash(request_body: bytes) -> str:
    digest = hashlib.sha256(request_body).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _normalize_hex(value: str) -> str:
    return "".join(
        character for character in value.casefold() if character in "0123456789abcdef"
    )


def _certificate_digest_to_hex(value: str) -> str:
    normalized = _normalize_hex(value)
    if len(normalized) == 64:
        return normalized
    try:
        padded = value + "=" * ((4 - len(value) % 4) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        return ""
    return decoded.hex() if len(decoded) == 32 else ""
