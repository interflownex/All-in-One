import subprocess

PROJECT_ID = "all-in-one-498012"


def create_secret(secret_id, payload):
    print(f"🏷️ Processando segredo: {secret_id}...")

    # 1. Tentar criar o segredo
    create_cmd = [
        "gcloud",
        "secrets",
        "create",
        secret_id,
        "--replication-policy=automatic",
        "--project",
        PROJECT_ID,
    ]
    subprocess.run(create_cmd, capture_output=True)

    # 2. Adicionar versão
    add_cmd = [
        "gcloud",
        "secrets",
        "versions",
        "add",
        secret_id,
        "--data-file=-",
        "--project",
        PROJECT_ID,
    ]
    # Passando payload como string e usando text=True
    result = subprocess.run(add_cmd, input=payload, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Versão adicionada para {secret_id}")
    else:
        print(f"❌ Erro ao adicionar versão para {secret_id}: {result.stderr}")


if __name__ == "__main__":
    secrets = {
        "identity-dsn": "postgresql://all-in-one-user:strong-password@all-in-one-cluster.us-central1.alloydb.goog/identity_db",
        "jwt-secret": "super-secret-key-for-auth-gateway-all-in-one",
        "document-encryption-key": "base64-32-chars-long-encryption-key-for-jobs",
    }

    print(f"🚀 Iniciando configuração de segredos via gcloud no projeto {PROJECT_ID}\n")
    for sid, val in secrets.items():
        create_secret(sid, val)
    print("\n🏁 Finalizado.")
