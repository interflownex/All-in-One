import subprocess
import sys

# Configurações GCP
PROJECT_ID = "all-in-one-498012"
REPOSITORY = "all-in-one-repo"
LOCATION = "us-central1"
REGISTRY_URL = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}"

# Módulos principais para build rápido
CORE_MODULES = ["identity", "api-hub", "jobs", "business", "finance"]

# Todos os módulos baseados no docker-compose
ALL_MODULES = [
    "api-hub", "identity", "business", "finance", "marketplace", "stock",
    "delivery", "services", "mobility", "erp", "wms", "tms", "crm", "health",
    "jobs", "property", "outbox-dispatcher", "retention-worker"
]

def run_command(cmd: list[str]) -> bool:
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"Erro ao executar comando. Código: {result.returncode}")
        return False
    return True

def build_and_push(modules, tag="latest"):
    print(f"\n🚀 Iniciando Build & Push para GCP: {REGISTRY_URL}\n")
    
    # 1. Build local usando docker compose
    print("📦 Passo 1: Construindo imagens localmente...")
    build_cmd = ["docker", "compose", "-f", "infra/docker/docker-compose.yml", "build"] + modules
    if not run_command(build_cmd):
        return

    # 2. Tag e Push
    for module in modules:
        local_image = f"all-in-one-{module}"
        remote_image = f"{REGISTRY_URL}/{module}:{tag}"
        
        print(f"\n🏷️  Tagueando {module}...")
        if not run_command(["docker", "tag", local_image, remote_image]):
            continue
            
        print(f"📤 Enviando {module} para Artifact Registry...")
        run_command(["docker", "push", remote_image])

    print("\n✅ Processo concluído.")

if __name__ == "__main__":
    choice = "core"
    if len(sys.argv) > 1:
        choice = sys.argv[1].lower()
    
    modules_to_build = CORE_MODULES if choice == "core" else ALL_MODULES
    build_and_push(modules_to_build)
