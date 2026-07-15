from pathlib import Path
import sys
from typing import Any
from uuid import UUID, uuid4
from fastapi import Body, Request, HTTPException, Depends
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.domain_rules import check_payload
from shared.runtime import create_module_app
from auth_logic import (
    LoginRequest, 
    TokenResponse, 
    TelemetryClient, 
    verify_password, 
    create_access_token,
    get_password_hash
)
from kyc_mfa_models import KYCSubmission, KYCStatus, MFASetup, MFAVerification

app = create_module_app("identity")
telemetry = TelemetryClient()

app.router.routes = [
    route
    for route in app.router.routes
    if not (getattr(route, "path", None) == "/registrations" and "POST" in getattr(route, "methods", set()))
]

@app.post("/kyc/submit", status_code=202)
async def submit_kyc(
    body: KYCSubmission, 
    request: Request
) -> Any:
    store = app.extra["store"]
    
    payload = {
        "biometry_hash": body.biometry_hash,
        "doc_front_url": "pending_upload",
        "doc_back_url": "pending_upload"
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
            body.idempotency_key
        )
        
        await telemetry.log_access(
            str(body.user_id), 
            "kyc_submission", 
            "processing", 
            request.client.host,
            metadata={"record_id": record["id"]}
        )
        
        return {
            "record_id": record["id"],
            "status": "PROCESSING",
            "message": "Validacao biometrica e documental em analise."
        }
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Erro ao submeter KYC: {exc}")

@app.get("/kyc/status/{user_id}", response_model=KYCStatus)
async def get_kyc_status(user_id: UUID) -> Any:
    store = app.extra["store"]
    records = store.list("kyc_records", str(user_id))
    
    if not records:
        raise HTTPException(status_code=404, detail="Nenhum registro de KYC encontrado para este usuario.")
    
    latest = records[0]
    
    return {
        "record_id": latest["id"],
        "user_id": latest["user_id"],
        "status": latest["status"],
        "risk_score": latest["payload"].get("risk_score"),
        "reason": latest["payload"].get("decision_reason")
    }

@app.post("/mfa/setup")
async def setup_mfa(body: MFASetup, request: Request):
    await telemetry.log_access(str(body.user_id), "mfa_setup_init", body.method, request.client.host)
    
    if body.method == "sms":
        return {
            "method": "sms",
            "message": "Um código de 6 dígitos foi enviado via SMS (simulado).",
            "status": "pending_verification"
        }
    
    return {
        "method": body.method,
        "secret": "JBSWY3DPEHPK3PXP",
        "qr_code_url": f"otpauth://totp/AllInOne?secret=JBSWY3DPEHPK3PXP&issuer=AllInOneID",
        "status": "pending_verification"
    }

@app.post("/mfa/verify")
async def verify_mfa(body: MFAVerification, request: Request):
    if body.code == "123456":
        await telemetry.log_access(str(body.user_id), "mfa_verify", "success", request.client.host)
        return {"status": "verified"}
    
    await telemetry.log_access(str(body.user_id), "mfa_verify", "failed", request.client.host)
    raise HTTPException(status_code=401, detail="Codigo MFA invalido.")

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
            "birth_date": "1990-01-01"
        },
        "authenticity_score": 0.98,
        "source": "mock_google_vision"
    }


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, 
    request: Request
) -> Any:
    store = app.state.store if hasattr(app.state, "store") else None
    
    users = app.extra["store"].list("users")
    user = next((u for u in users if u["payload"].get("email") == body.email), None)
    
    if not user:
        await telemetry.log_access("unknown", "login_attempt", "failed_user_not_found", request.client.host)
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")
    
    if not verify_password(body.password, user["payload"].get("password_hash", "")):
        await telemetry.log_access(user["id"], "login_attempt", "failed_wrong_password", request.client.host)
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")
    
    if user["status"] == "BLOCKED":
        await telemetry.log_access(user["id"], "login_attempt", "failed_blocked", request.client.host)
        raise HTTPException(status_code=403, detail="Conta bloqueada.")

    token_data = {
        "sub": user["id"],
        "email": user["payload"]["email"],
        "roles": user["payload"].get("roles", [])
    }
    access_token, expires_at = create_access_token(token_data)
    
    await telemetry.log_access(
        user["id"], 
        "login_success", 
        "success", 
        request.client.host, 
        request.headers.get("user-agent")
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "expires_at": expires_at.isoformat()
    }

@app.post("/auth/logout")
async def logout(request: Request, user_id: str):
    await telemetry.log_access(user_id, "logout", "success", request.client.host)
    return {"message": "Logout registrado."}

@app.post("/registrations", status_code=201)
async def register_user_with_hash(request: Request, body: dict[str, Any] = Body(...)):
    payload = body.model_dump() if hasattr(body, "model_dump") else dict(body)
    user_id = str(payload.get("id") or uuid4())
    payload["id"] = user_id
    if "cpf_document" not in payload and payload.get("document_cpf"):
        payload["cpf_document"] = payload["document_cpf"]
    if "document_cpf" not in payload and payload.get("cpf_document"):
        payload["document_cpf"] = payload["cpf_document"]
    payload.setdefault("birth_date", "1990-01-01")
    payload.setdefault("phone_e164", f"+55{str(int(user_id.replace('-', '')[:10], 16))[-10:]}")
    payload.setdefault("face_hash", f"face-{user_id}")
    payload.setdefault("liveness_score", 0.9999)
    payload["password_hash"] = get_password_hash(payload.pop("password_hash", "temporary-registration-password"))
    
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
        await telemetry.log_access(user["id"], "registration", "success", request.client.host)
        return user
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Erro no cadastro: {exc}")
