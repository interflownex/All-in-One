#!/usr/bin/env python3
"""
Monitora e higieniza o armazenamento GCP.
Limite: 5GB. Gatilho: 85% (4.25GB).
Execução persistente e mandatória.
"""
from __future__ import annotations
import subprocess
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="[GCP Hygiene] %(message)s")

MAX_GB = 5.0
THRESHOLD_PERCENT = 0.85
MAX_MB = MAX_GB * 1024
THRESHOLD_MB = MAX_MB * THRESHOLD_PERCENT

PROJECT_ID = "all-in-one-498012"
LOCATION = "us-central1"
REPO_NAME = "all-in-one-repo"

def run_cmd(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip()

def get_artifact_registry_size_mb() -> float:
    cmd = [
        "gcloud", "artifacts", "repositories", "list",
        f"--project={PROJECT_ID}",
        f"--location={LOCATION}",
        "--format=json"
    ]
    stdout = run_cmd(cmd)
    if not stdout:
        return 0.0
    try:
        repos = json.loads(stdout)
        total_bytes = sum(int(repo.get("sizeBytes", 0)) for repo in repos)
        return total_bytes / (1024 * 1024)
    except Exception:
        return 0.0

def get_cloud_build_bucket_size_mb() -> float:
    cmd = [
        "gcloud", "storage", "du", "-s",
        f"gs://{PROJECT_ID}_cloudbuild/"
    ]
    stdout = run_cmd(cmd)
    if not stdout:
        return 0.0
    try:
        bytes_str = stdout.split()[0]
        return float(bytes_str) / (1024 * 1024)
    except Exception:
        return 0.0

def clean_artifact_registry() -> None:
    logging.info("Iniciando limpeza no Artifact Registry (Removendo imagens sem tag)...")
    repos = [
        "ai-core", "api-hub", "bi", "bpm", "business", "crm", "delivery", 
        "document", "erp", "finance", "health", "hr", "identity", "jobs", 
        "legal", "marketplace", "mobility", "outbox-dispatcher", "permissions", 
        "property", "retention-worker", "riders", "services", "stock", "tms", 
        "vision", "wms"
    ]
    for repo in repos:
        cmd_list = [
            "gcloud", "artifacts", "docker", "images", "list",
            f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{repo}",
            "--filter=NOT tags:*",
            "--format=get(version)"
        ]
        out = run_cmd(cmd_list)
        if not out:
            continue
        for version in out.splitlines():
            if version:
                img_path = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{repo}@{version}"
                run_cmd(["gcloud", "artifacts", "docker", "images", "delete", img_path, "--quiet"])

def clean_cloud_build_bucket() -> None:
    logging.info("Iniciando limpeza no Cloud Storage (Removendo pacotes fonte antigos)...")
    run_cmd(["gcloud", "storage", "rm", f"gs://{PROJECT_ID}_cloudbuild/source/*.tgz"])

def main() -> int:
    logging.info("Verificando armazenamento do Google Cloud...")
    ar_size = get_artifact_registry_size_mb()
    gcs_size = get_cloud_build_bucket_size_mb()
    total_size = ar_size + gcs_size
    
    logging.info(f"Artifact Registry: {ar_size:.2f} MB | Cloud Storage (Build): {gcs_size:.2f} MB")
    logging.info(f"Tamanho Total Estimado: {total_size:.2f} MB / Limite Estipulado: {MAX_MB:.2f} MB")
    
    if total_size >= THRESHOLD_MB:
        logging.warning(f"Capacidade em {total_size/MAX_MB*100:.1f}% (> 85%). Gatilho de Higienizacao ativado!")
        clean_cloud_build_bucket()
        clean_artifact_registry()
        
        ar_size = get_artifact_registry_size_mb()
        gcs_size = get_cloud_build_bucket_size_mb()
        new_total = ar_size + gcs_size
        logging.info(f"Limpeza concluida. Novo tamanho total: {new_total:.2f} MB")
    else:
        logging.info("Armazenamento seguro (Abaixo de 85%). Nenhuma acao destrutiva necessaria.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
