import asyncio
import os
import uuid
from datetime import datetime

import httpx
import pytest

BASE_URL = os.environ.get("IDENTITY_E2E_URL", "http://localhost:8101")


def test_identity_e2e_flow():
    asyncio.run(_test_identity_e2e_flow())


async def _test_identity_e2e_flow():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=3.0) as client:
        try:
            health_resp = await client.get("/health")
        except httpx.HTTPError as exc:
            pytest.skip(f"Identity E2E indisponivel em {BASE_URL}: {exc}")
        if health_resp.status_code != 200:
            pytest.skip(
                f"Identity E2E indisponivel em {BASE_URL}: HTTP {health_resp.status_code}"
            )

    user_email = f"test_{uuid.uuid4().hex[:8]}@allinone.com"
    user_password = "SecurePassword123!"
    user_id = str(uuid.uuid4())
    document_cpf = f"CPF-{uuid.uuid4().hex[:12]}"

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        reg_payload = {
            "id": user_id,
            "full_name": "Test User E2E",
            "email": user_email,
            "password_hash": user_password,
            "document_cpf": document_cpf,
            "terms_accepted_at": datetime.now().isoformat(),
            "lgpd_consent_at": datetime.now().isoformat(),
        }
        reg_resp = await client.post("/registrations", json=reg_payload)
        assert reg_resp.status_code == 201
        print("✓ Cadastro realizado")

        login_payload = {"email": user_email, "password": user_password}
        login_resp = await client.post("/auth/login", json=login_payload)
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        print("✓ Login realizado (JWT gerado)")

        headers = {"Authorization": f"Bearer {token}", "X-Actor-User-Id": user_id}
        kyc_payload = {
            "user_id": user_id,
            "biometry_hash": "a" * 32,
            "idempotency_key": f"idemp_{uuid.uuid4().hex}",
        }
        kyc_resp = await client.post("/kyc/submit", json=kyc_payload, headers=headers)
        assert kyc_resp.status_code == 202
        print("✓ KYC submetido")

        status_resp = await client.get(f"/kyc/status/{user_id}", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "PROCESSING"
        print("✓ Status KYC validado")

        mfa_setup_payload = {"user_id": user_id, "method": "totp"}
        mfa_resp = await client.post(
            "/mfa/setup", json=mfa_setup_payload, headers=headers
        )
        assert mfa_resp.status_code == 200
        assert "secret" in mfa_resp.json()
        print("✓ MFA Setup iniciado")


if __name__ == "__main__":
    asyncio.run(_test_identity_e2e_flow())
