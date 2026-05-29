from pathlib import Path
import sys
from typing import Any
from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

@app.post("/kyc/submit", status_code=202)
async def submit_kyc(
    body: KYCSubmission, 
    request: Request
) -> Any:
    store = app.extra["store"]
    
    # Payload para o banco de dados
    payload = {
        "biometry_hash": body.biometry_hash,
        "doc_front_url": "pending_upload", # Em produção, aqui seria gerada uma URL pré-assinada de S3
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
    
    latest = records[0] # Lista ordenada por data decrescente
    
    return {
        "record_id": latest["id"],
        "user_id": latest["user_id"],
        "status": latest["status"],
        "risk_score": latest["payload"].get("risk_score"),
        "reason": latest["payload"].get("decision_reason")
    }

@app.post("/mfa/setup")
async def setup_mfa(body: MFASetup, request: Request):
    # Stub para configuração de MFA
    await telemetry.log_access(str(body.user_id), "mfa_setup_init", body.method, request.client.host)
    return {
        "method": body.method,
        "secret": "JBSWY3DPEHPK3PXP", # Exemplo de segredo TOTP
        "qr_code_url": f"otpauth://totp/AllInOne?secret=JBSWY3DPEHPK3PXP&issuer=AllInOneID",
        "status": "pending_verification"
    }

@app.post("/mfa/verify")
async def verify_mfa(body: MFAVerification, request: Request):
    # Stub para verificação de MFA
    if body.code == "123456": # Mock de validação
        await telemetry.log_access(str(body.user_id), "mfa_verify", "success", request.client.host)
        return {"status": "verified"}
    
    await telemetry.log_access(str(body.user_id), "mfa_verify", "failed", request.client.host)
    raise HTTPException(status_code=401, detail="Codigo MFA invalido.")


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, 
    request: Request
) -> Any:
    # O store_for("identity") retorna o IdentityPostgresStore configurado no runtime
    store = app.state.store if hasattr(app.state, "store") else None
    
    # Busca usuário pelo e-mail (usando a lista filtrada do Store)
    users = app.extra["store"].list("users") # O create_module_app expõe o store via closure ou extra em alguns contextos, vamos garantir acesso
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

    # Gera o Token
    token_data = {
        "sub": user["id"],
        "email": user["payload"]["email"],
        "roles": user["payload"].get("roles", [])
    }
    access_token, expires_at = create_access_token(token_data)
    
    # Telemetria de sucesso
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

# Sobrescrevendo a lógica de criação de usuário para usar hash de senha real
@app.post("/registrations", status_code=201)
async def register_user_with_hash(body: Any, request: Request):
    payload = body.model_dump()
    payload["password_hash"] = get_password_hash(payload.pop("password_hash"))
    
    store = app.extra["store"]
    rule = app.extra["rule_for"]("identity", "users")
    
    try:
        user = store.create(
            "users",
            payload.get("id", str(sys.modules['uuid'].uuid4())),
            None,
            rule.initial_status,
            payload,
            "self_registration",
            rule.unique_fields,
            "identity.user.created",
            None,
        )
        await telemetry.log_access(user["id"], "registration", "success", request.client.host)
        return user
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Erro no cadastro: {exc}")

