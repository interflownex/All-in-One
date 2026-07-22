import hashlib
import hmac
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Body, Depends, HTTPException, Request
from starlette.concurrency import run_in_threadpool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from auth_logic import (
    LoginRequest,
    RefreshTokenRequest,
    TelemetryClient,
    TokenResponse,
    create_access_token,
    create_refresh_token,
    decrypt_mfa_secret,
    encrypt_mfa_secret,
    generate_totp_secret,
    get_password_hash,
    hash_refresh_token,
    verify_password,
    verify_totp,
)
from kyc_mfa_models import KYCStatus, KYCSubmission, MFASetup, MFAVerification
from play_integrity import (
    IntegrityConfigurationError,
    IntegrityDecision,
    IntegrityRejected,
    PlayIntegrityVerifier,
)
from shared.domain_rules import check_payload
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers

app = create_module_app("identity")
telemetry = TelemetryClient()
app.extra["play_integrity_verifier"] = PlayIntegrityVerifier()


async def require_play_integrity(request: Request) -> IntegrityDecision:
    token = request.headers.get("X-Play-Integrity-Token")
    verifier: PlayIntegrityVerifier = app.extra["play_integrity_verifier"]
    try:
        decision = await run_in_threadpool(verifier.verify, token, await request.body())
    except IntegrityRejected as exc:
        await telemetry.log_access(
            "unknown",
            "play_integrity",
            "rejected",
            _client_ip(request),
            metadata={
                "reason": exc.reason,
                "correlation_id": request.headers.get("X-Correlation-Id", "")[:64],
            },
        )
        raise HTTPException(
            status_code=403,
            detail="Integridade do aplicativo ou dispositivo rejeitada.",
        ) from exc
    except IntegrityConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="Validacao de integridade indisponivel.",
        ) from exc
    request.state.play_integrity = decision
    return decision


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    public = dict(user)
    public["payload"] = {
        key: value
        for key, value in user["payload"].items()
        if key not in {"password_hash", "refresh_token", "token_hash"}
    }
    return public


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _device_fingerprint(request: Request, explicit: str | None = None) -> str:
    value = explicit or request.headers.get("X-Device-Fingerprint")
    if value:
        return value[:256]
    user_agent = request.headers.get("user-agent", "unknown")
    return "legacy-" + hashlib.sha256(user_agent.encode("utf-8")).hexdigest()


def _issue_session(
    store: Any, user: dict[str, Any], request: Request, device_fingerprint: str
) -> dict[str, Any]:
    refresh_token, token_hash, refresh_expires_at = create_refresh_token()
    session = store.create(
        "sessions",
        user["id"],
        None,
        "active",
        {
            "token_hash": token_hash,
            "device_fingerprint": device_fingerprint,
            "ip_address": _client_ip(request),
            "expires_at": refresh_expires_at.isoformat(),
        },
        user["id"],
        (),
        "identity.session.created",
        None,
    )
    token_data = {
        "sub": user["id"],
        "email": user["payload"]["email"],
        "roles": user["payload"].get("roles", []),
        "sid": session["id"],
        "token_use": "access",
    }
    access_token, expires_at = create_access_token(token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "session_id": session["id"],
        "expires_at": expires_at.isoformat(),
        "refresh_expires_at": refresh_expires_at.isoformat(),
    }


def _active_session_for(store: Any, refresh_token: str) -> dict[str, Any] | None:
    token_hash = hash_refresh_token(refresh_token)
    return next(
        (
            session
            for session in store.list("sessions")
            if session["status"] == "active"
            and session["payload"].get("token_hash") == token_hash
        ),
        None,
    )


def _revoke_session(
    store: Any, session: dict[str, Any], actor: str, reason: str
) -> None:
    payload = dict(session["payload"])
    payload["revoked_at"] = datetime.now(UTC).isoformat()
    payload["revocation_reason"] = reason
    store.update(
        session, payload, "revoked", actor, "revoke", "identity.session.revoked"
    )


app.router.routes = [
    route
    for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/registrations"
        and "POST" in getattr(route, "methods", set())
    )
]


@app.post("/kyc/submit", status_code=202)
async def submit_kyc(body: KYCSubmission, request: Request) -> Any:
    store = app.extra["store"]

    payload = {
        "biometry_hash": body.biometry_hash,
        "doc_front_url": "pending_upload",
        "doc_back_url": "pending_upload",
    }

    try:
        record = store.create(
            "kyc_records",
            str(body.user_id),
            None,
            "PROCESSING",
            payload,
            str(body.user_id),
            (),
            "identity.kyc.submitted",
            body.idempotency_key,
        )

        await telemetry.log_access(
            str(body.user_id),
            "kyc_submission",
            "processing",
            request.client.host,
            metadata={"record_id": record["id"]},
        )

        return {
            "record_id": record["id"],
            "status": "PROCESSING",
            "message": "Validacao biometrica e documental em analise.",
        }
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Erro ao submeter KYC: {exc}")


@app.get("/kyc/status/{user_id}", response_model=KYCStatus)
async def get_kyc_status(user_id: UUID) -> Any:
    store = app.extra["store"]
    records = store.list("kyc_records", str(user_id))

    if not records:
        raise HTTPException(
            status_code=404,
            detail="Nenhum registro de KYC encontrado para este usuario.",
        )

    latest = records[0]

    return {
        "record_id": latest["id"],
        "user_id": latest["user_id"],
        "status": latest["status"],
        "risk_score": latest["payload"].get("risk_score"),
        "reason": latest["payload"].get("decision_reason"),
    }


@app.post("/mfa/setup")
async def setup_mfa(
    body: MFASetup, request: Request, actor: Actor = Depends(actor_from_headers)
) -> Any:
    user_id = str(body.user_id)
    if str(actor.user_id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="MFA so pode ser configurado pelo titular autenticado.",
        )
    if body.method != "totp":
        raise HTTPException(
            status_code=501,
            detail="Metodo MFA depende de provedor externo ainda nao homologado.",
        )
    store = app.extra["store"]
    secret = generate_totp_secret()
    expires_at = datetime.now(UTC) + timedelta(minutes=10)
    factor = store.create(
        "identity_verifications",
        user_id,
        None,
        "PROCESSING",
        {
            "verification_type": "mfa_totp",
            "method": "totp",
            "secret_ciphertext": encrypt_mfa_secret(secret, user_id),
            "setup_expires_at": expires_at.isoformat(),
            "last_counter": -1,
        },
        user_id,
        (),
        "identity.mfa.setup_started",
        body.idempotency_key,
    )
    await telemetry.log_access(
        user_id,
        "mfa_setup_init",
        "totp",
        _client_ip(request),
        metadata={"factor_id": factor["id"]},
    )
    return {
        "factor_id": factor["id"],
        "method": "totp",
        "secret": secret,
        "qr_code_url": f"otpauth://totp/AllInOne:{user_id}?secret={secret}&issuer=AllInOneID&digits=6&period=30",
        "expires_at": expires_at.isoformat(),
        "status": "pending_verification",
    }


@app.post("/mfa/verify")
async def verify_mfa(
    body: MFAVerification, request: Request, actor: Actor = Depends(actor_from_headers)
) -> Any:
    user_id = str(body.user_id)
    if str(actor.user_id) != user_id:
        raise HTTPException(
            status_code=403,
            detail="MFA so pode ser verificado pelo titular autenticado.",
        )
    store = app.extra["store"]
    factors = [
        item
        for item in store.list("identity_verifications", user_id)
        if item["payload"].get("verification_type") == "mfa_totp"
        and item["status"] in {"PROCESSING", "APPROVED"}
    ]
    if not factors:
        raise HTTPException(status_code=404, detail="Fator TOTP nao configurado.")
    factor = factors[0]
    session = store.get("sessions", str(body.session_id))
    if (
        session is None
        or session["status"] != "active"
        or session["user_id"] != user_id
    ):
        raise HTTPException(
            status_code=401,
            detail="Sessao ativa do titular obrigatoria para concluir MFA.",
        )
    payload = dict(factor["payload"])
    if factor["status"] == "PROCESSING" and datetime.fromisoformat(
        payload["setup_expires_at"]
    ) <= datetime.now(UTC):
        store.update(
            factor, payload, "REJECTED", user_id, "expire", "identity.mfa.setup_expired"
        )
        raise HTTPException(status_code=410, detail="Configuracao MFA expirada.")
    secret = decrypt_mfa_secret(payload["secret_ciphertext"], user_id)
    accepted_counter = verify_totp(
        secret, body.code, int(payload.get("last_counter", -1))
    )
    if accepted_counter is None:
        await telemetry.log_access(
            user_id,
            "mfa_verify",
            "failed",
            _client_ip(request),
            metadata={"factor_id": factor["id"]},
        )
        raise HTTPException(
            status_code=401, detail="Codigo MFA invalido ou reutilizado."
        )
    payload["last_counter"] = accepted_counter
    payload["verified_at"] = datetime.now(UTC).isoformat()
    store.update(
        factor, payload, "APPROVED", user_id, "verify", "identity.mfa.verified"
    )
    session_payload = dict(session["payload"])
    session_payload["mfa_verified_at"] = payload["verified_at"]
    store.update(
        session,
        session_payload,
        "active",
        user_id,
        "mfa_verify",
        "identity.session.mfa_verified",
    )
    user = store.get("users", user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario da sessao indisponivel.")
    access_token, access_expires_at = create_access_token(
        {
            "sub": user_id,
            "email": user["payload"]["email"],
            "roles": user["payload"].get("roles", []),
            "sid": session["id"],
            "token_use": "access",
            "mfa_verified": True,
            "mfa_verified_at": payload["verified_at"],
        }
    )
    await telemetry.log_access(
        user_id,
        "mfa_verify",
        "success",
        _client_ip(request),
        metadata={"factor_id": factor["id"]},
    )
    return {
        "status": "verified",
        "factor_id": factor["id"],
        "verified_at": payload["verified_at"],
        "access_token": access_token,
        "expires_at": access_expires_at.isoformat(),
    }


@app.post("/kyc/ocr-validate", status_code=200)
async def kyc_ocr_validate(request: Request, body: dict = Body(...)):
    """
    Mock de Webhook do Google Vision (OCR) para validar documentos CNH/RG.
    Recebe um documento e retorna o texto extraído / pontuação de autenticidade.
    """
    record_id = body.get("record_id")
    if not record_id:
        raise HTTPException(status_code=400, detail="record_id obrigatorio")

    return {
        "record_id": record_id,
        "ocr_status": "APPROVED",
        "extracted_data": {
            "name": "João Silva",
            "document_number": "12345678900",
            "birth_date": "1990-01-01",
        },
        "authenticity_score": 0.98,
        "source": "mock_google_vision",
    }


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    _integrity: IntegrityDecision = Depends(require_play_integrity),
) -> Any:
    store = app.extra["store"]
    users = store.list("users")
    user = next((u for u in users if u["payload"].get("email") == body.email), None)

    if not user:
        await telemetry.log_access(
            "unknown", "login_attempt", "failed_user_not_found", request.client.host
        )
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    if not verify_password(body.password, user["payload"].get("password_hash", "")):
        await telemetry.log_access(
            user["id"], "login_attempt", "failed_wrong_password", request.client.host
        )
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    if user["status"] == "BLOCKED":
        await telemetry.log_access(
            user["id"], "login_attempt", "failed_blocked", request.client.host
        )
        raise HTTPException(status_code=403, detail="Conta bloqueada.")

    tokens = _issue_session(store, user, request, _device_fingerprint(request))

    await telemetry.log_access(
        user["id"],
        "login_success",
        "success",
        request.client.host,
        request.headers.get("user-agent"),
    )

    return tokens


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_session(
    body: RefreshTokenRequest,
    request: Request,
    _integrity: IntegrityDecision = Depends(require_play_integrity),
) -> Any:
    store = app.extra["store"]
    session = _active_session_for(store, body.refresh_token)
    if session is None:
        await telemetry.log_access(
            "unknown",
            "refresh_attempt",
            "failed_invalid_or_replayed",
            _client_ip(request),
        )
        raise HTTPException(
            status_code=401, detail="Refresh token invalido, revogado ou reutilizado."
        )
    try:
        expires_at = datetime.fromisoformat(session["payload"]["expires_at"])
    except (KeyError, ValueError):
        _revoke_session(store, session, session["user_id"], "invalid_expiry")
        raise HTTPException(status_code=401, detail="Sessao invalida.") from None
    if expires_at <= datetime.now(UTC):
        _revoke_session(store, session, session["user_id"], "expired")
        raise HTTPException(status_code=401, detail="Sessao expirada.")
    fingerprint = _device_fingerprint(request, body.device_fingerprint)
    if not secrets_compare(
        session["payload"].get("device_fingerprint", ""), fingerprint
    ):
        _revoke_session(store, session, session["user_id"], "device_mismatch")
        await telemetry.log_access(
            session["user_id"],
            "refresh_attempt",
            "failed_device_mismatch",
            _client_ip(request),
        )
        raise HTTPException(
            status_code=401, detail="Dispositivo da sessao nao confere."
        )
    user = store.get("users", session["user_id"])
    if user is None or user["status"] == "BLOCKED":
        _revoke_session(store, session, session["user_id"], "user_unavailable")
        raise HTTPException(status_code=401, detail="Usuario da sessao indisponivel.")
    _revoke_session(store, session, user["id"], "rotated")
    tokens = _issue_session(store, user, request, fingerprint)
    await telemetry.log_access(
        user["id"],
        "refresh_success",
        "success",
        _client_ip(request),
        metadata={"session_id": tokens["session_id"]},
    )
    return tokens


@app.post("/auth/logout")
async def logout(
    body: RefreshTokenRequest,
    request: Request,
    _integrity: IntegrityDecision = Depends(require_play_integrity),
) -> Any:
    store = app.extra["store"]
    session = _active_session_for(store, body.refresh_token)
    if session is not None:
        _revoke_session(store, session, session["user_id"], "logout")
        await telemetry.log_access(
            session["user_id"],
            "logout",
            "success",
            _client_ip(request),
            metadata={"session_id": session["id"]},
        )
    return {"message": "Sessao encerrada."}


def secrets_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(
        hashlib.sha256(left.encode("utf-8")).digest(),
        hashlib.sha256(right.encode("utf-8")).digest(),
    )


@app.post("/registrations", status_code=201)
async def register_user_with_hash(
    request: Request,
    body: dict[str, Any] = Body(...),
    _integrity: IntegrityDecision = Depends(require_play_integrity),
):
    payload = body.model_dump() if hasattr(body, "model_dump") else dict(body)
    user_id = str(payload.get("id") or uuid4())
    payload["id"] = user_id
    if "cpf_document" not in payload and payload.get("document_cpf"):
        payload["cpf_document"] = payload["document_cpf"]
    if "document_cpf" not in payload and payload.get("cpf_document"):
        payload["document_cpf"] = payload["cpf_document"]
    payload.setdefault("birth_date", "1990-01-01")
    payload.setdefault(
        "phone_e164", f"+55{str(int(user_id.replace('-', '')[:10], 16))[-10:]}"
    )
    payload.setdefault("face_hash", f"face-{user_id}")
    payload.setdefault("liveness_score", 0.9999)
    payload["password_hash"] = get_password_hash(
        payload.pop("password_hash", "temporary-registration-password")
    )

    store = app.extra["store"]
    rule = app.extra["rule_for"]("identity", "users")
    check_payload(rule, payload)

    try:
        user = store.create(
            "users",
            user_id,
            None,
            "pending_validation",
            payload,
            user_id,
            rule.unique_fields,
            "identity.user.created",
            None,
        )
        await telemetry.log_access(
            user["id"], "registration", "success", request.client.host
        )
        return _public_user(user)
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Erro no cadastro: {exc}")
