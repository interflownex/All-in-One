import subprocess
import sys

PROJECT_ID = "all-in-one-498012"
REPOSITORY = "all-in-one-repo"
LOCATION = "us-central1"
REGISTRY_URL = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}"

TARGET_IMAGES = [
    "ai-core",
    "api-hub",
    "bi",
    "bpm",
    "business",
    "crm",
    "delivery",
    "document",
    "erp",
    "finance",
    "health",
    "hr",
    "identity",
    "jobs",
    "legal",
    "marketplace",
    "mobility",
    "permissions",
    "property",
    "riders",
    "services",
    "stock",
    "tms",
    "vision",
    "wms",
    "outbox-dispatcher",
    "retention-worker",
]


def check_images():
    print(
        f"🔍 Validando {len(TARGET_IMAGES)} imagens no Artifact Registry: {REGISTRY_URL}\n"
    )

    missing = []
    found_count = 0

    for img in TARGET_IMAGES:
        full_path = f"{REGISTRY_URL}/{img}:latest"
        # Comando para verificar se a tag existe
        cmd = [
            "gcloud",
            "artifacts",
            "docker",
            "images",
            "describe",
            full_path,
            "--format=json",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {img}:latest - OK")
            found_count += 1
        else:
            print(f"❌ {img}:latest - NÃO ENCONTRADA")
            missing.append(img)

    print(f"\n📊 Resumo: {found_count}/{len(TARGET_IMAGES)} imagens validadas.")

    if missing:
        print(f"⚠️ Imagens ausentes: {', '.join(missing)}")
        return False

    print("🚀 Todas as imagens estão prontas para o deploy!")
    return True


if __name__ == "__main__":
    success = check_images()
    if not success:
        sys.exit(1)
