import os

PROJECT_ID = "all-in-one-498012"
REPOSITORY = "all-in-one-repo"
LOCATION = "us-central1"
REGISTRY_URL = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPOSITORY}"

dockerfiles = [
    "./modules/ai_core/Dockerfile",
    "./modules/api_hub/Dockerfile",
    "./modules/bi/Dockerfile",
    "./modules/bpm/Dockerfile",
    "./modules/business/Dockerfile",
    "./modules/crm/Dockerfile",
    "./modules/delivery/Dockerfile",
    "./modules/document/Dockerfile",
    "./modules/erp/Dockerfile",
    "./modules/finance/Dockerfile",
    "./modules/health/Dockerfile",
    "./modules/hr/Dockerfile",
    "./modules/identity/Dockerfile",
    "./modules/jobs/Dockerfile",
    "./modules/legal/Dockerfile",
    "./modules/marketplace/Dockerfile",
    "./modules/mobility/Dockerfile",
    "./modules/permissions/Dockerfile",
    "./modules/property/Dockerfile",
    "./modules/riders/Dockerfile",
    "./modules/services/Dockerfile",
    "./modules/stock/Dockerfile",
    "./modules/tms/Dockerfile",
    "./modules/vision/Dockerfile",
    "./modules/wms/Dockerfile",
    "./workers/outbox_dispatcher/Dockerfile",
    "./workers/retention_worker/Dockerfile"
]

yaml_content = ["steps:"]
images = []

for df in dockerfiles:
    # Extrair nome do serviço do caminho do Dockerfile
    if "modules" in df:
        service_name = df.split("/")[2].replace("_", "-")
    else:
        service_name = df.split("/")[2].replace("_", "-")
        
    image_tag = f"{REGISTRY_URL}/{service_name}:latest"
    images.append(image_tag)
    
    yaml_content.append(f"  # {service_name}")
    yaml_content.append(f"  - name: 'gcr.io/cloud-builders/docker'")
    yaml_content.append(f"    args: ['build', '-t', '{image_tag}', '-f', '{df}', '.']")

yaml_content.append("\nimages:")
for img in images:
    yaml_content.append(f"  - '{img}'")

yaml_content.append("\noptions:")
yaml_content.append("  logging: CLOUD_LOGGING_ONLY")
yaml_content.append("  machineType: 'E2_HIGHCPU_32' # Aumentando potência para build massivo")

with open("infra/ci-cd/cloudbuild-all.yaml", "w") as f:
    f.write("\n".join(yaml_content))

print("Manifesto infra/ci-cd/cloudbuild-all.yaml gerado com sucesso.")
