import pytest
import httpx
import uuid
from datetime import datetime

# Configurações de teste (ajustar conforme ambiente)
BASE_URL = "http://localhost:8101" # Porta do container identity no docker-compose

@pytest.mark.asyncio
async def test_identity_e2e_flow():
    user_email = f"test_{uuid.uuid4().hex[:8]}@allinone.com"
    user_password = "SecurePassword123!"
    user_id = str(uuid.uuid4())

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Registro de Usuário
        reg_payload = {
            "id": user_id,
            "full_name": "Test User E2E",
            "email": user_email,
            "password_hash": user_password,
            "document_cpf": "123.456.789-00",
            "terms_accepted_at": datetime.now().isoformat(),
            "lgpd_consent_at": datetime.now().isoformat()
        }
        reg_resp = await client.post("/registrations", json=reg_payload)
        assert reg_resp.status_code == 201
        print("✓ Cadastro realizado")

        # 2. Login
        login_payload = {
            "email": user_email,
            "password": user_password
        }
        login_resp = await client.post("/auth/login", json=login_payload)
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        print("✓ Login realizado (JWT gerado)")

        # 3. Submissão KYC
        headers = {"Authorization": f"Bearer {token}", "X-Actor-User-Id": user_id}
        kyc_payload = {
            "user_id": user_id,
            "biometry_hash": "a"*32, # Mock hash
            "idempotency_key": f"idemp_{uuid.uuid4().hex}"
        }
        kyc_resp = await client.post("/kyc/submit", json=kyc_payload, headers=headers)
        assert kyc_resp.status_code == 202
        print("✓ KYC submetido")

        # 4. Verificação de Status KYC
        status_resp = await client.get(f"/kyc/status/{user_id}", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "PROCESSING"
        print("✓ Status KYC validado")

        # 5. Configuração MFA
        mfa_setup_payload = {
            "user_id": user_id,
            "method": "totp"
        }
        mfa_resp = await client.post("/mfa/setup", json=mfa_setup_payload, headers=headers)
        assert mfa_resp.status_code == 200
        assert "secret" in mfa_resp.json()
        print("✓ MFA Setup iniciado")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_identity_e2e_flow())
