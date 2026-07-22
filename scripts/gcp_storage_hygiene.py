#!/usr/bin/env python3
"""
Monitora e higieniza o armazenamento GCP.
Limite: 5GB. Gatilho: 85% (4.25GB).
Execução persistente e mandatória.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta

logging.basicConfig(level=logging.INFO, format="[GCP Hygiene] %(message)s")

MAX_GB = 5.0
THRESHOLD_PERCENT = 0.85
MAX_MB = MAX_GB * 1024
THRESHOLD_MB = MAX_MB * THRESHOLD_PERCENT

PROJECT_ID = "all-in-one-498012"
LOCATION = "us-central1"
REPO_NAME = "all-in-one-repo"
CLOUDBUILD_SOURCE_RETENTION_DAYS = int(
    os.getenv("CLOUDBUILD_SOURCE_RETENTION_DAYS", "30")
)
CLOUDBUILD_SOURCE_KEEP_RECENT = int(os.getenv("CLOUDBUILD_SOURCE_KEEP_RECENT", "25"))


def run_cmd(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip()


def run_json(args: list[str]) -> list[dict]:
    stdout = run_cmd([*args, "--format=json"])
    if not stdout:
        return []
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else [data]


def parse_gcloud_datetime(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def object_url(item: dict) -> str | None:
    url = item.get("url") or item.get("name")
    if isinstance(url, str) and url.startswith("gs://"):
        return url
    bucket = item.get("bucket") or item.get("bucketName")
    name = item.get("name")
    if bucket and name:
        return f"gs://{bucket}/{name}"
    metadata = item.get("metadata")
    if isinstance(metadata, dict):
        bucket = metadata.get("bucket")
        name = metadata.get("name")
        if bucket and name:
            return f"gs://{bucket}/{name}"
    return str(url) if url else None


def object_updated_at(item: dict) -> datetime | None:
    metadata = item.get("metadata")
    candidates = [
        item.get("updateTime"),
        item.get("updated"),
        item.get("timeCreated"),
        item.get("creationTime"),
    ]
    if isinstance(metadata, dict):
        candidates.extend(
            [
                metadata.get("updated"),
                metadata.get("timeCreated"),
                metadata.get("creationTime"),
            ]
        )
    for candidate in candidates:
        parsed = parse_gcloud_datetime(str(candidate or ""))
        if parsed:
            return parsed
    return None


def get_artifact_registry_size_mb() -> float:
    cmd = [
        "gcloud",
        "artifacts",
        "repositories",
        "list",
        f"--project={PROJECT_ID}",
        f"--location={LOCATION}",
        "--format=json",
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
    cmd = ["gcloud", "storage", "du", "-s", f"gs://{PROJECT_ID}_cloudbuild/"]
    stdout = run_cmd(cmd)
    if not stdout:
        return 0.0
    try:
        bytes_str = stdout.split()[0]
        return float(bytes_str) / (1024 * 1024)
    except Exception:
        return 0.0


def clean_artifact_registry() -> None:
    logging.info(
        "Iniciando limpeza no Artifact Registry (Removendo imagens sem tag)..."
    )
    repos = [
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
        "outbox-dispatcher",
        "permissions",
        "property",
        "retention-worker",
        "riders",
        "services",
        "stock",
        "tms",
        "vision",
        "wms",
    ]
    for repo in repos:
        cmd_list = [
            "gcloud",
            "artifacts",
            "docker",
            "images",
            "list",
            f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{repo}",
            "--filter=NOT tags:*",
            "--format=get(version)",
        ]
        out = run_cmd(cmd_list)
        if not out:
            continue
        for version in out.splitlines():
            if version:
                img_path = f"{LOCATION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{repo}@{version}"
                run_cmd(
                    [
                        "gcloud",
                        "artifacts",
                        "docker",
                        "images",
                        "delete",
                        img_path,
                        "--quiet",
                    ]
                )


def clean_cloud_build_bucket() -> None:
    logging.info(
        "Iniciando limpeza segura no Cloud Storage (preservando pacotes fonte recentes)..."
    )
    objects = run_json(
        ["gcloud", "storage", "ls", f"gs://{PROJECT_ID}_cloudbuild/source/*.tgz"]
    )
    source_packages: list[tuple[datetime, str]] = []
    for item in objects:
        url = object_url(item)
        updated = object_updated_at(item)
        if url and updated:
            source_packages.append((updated, url))

    if not source_packages:
        logging.info("Nenhum pacote fonte antigo encontrado para limpeza.")
        return

    source_packages.sort(key=lambda entry: entry[0], reverse=True)
    cutoff = datetime.now(UTC) - timedelta(days=CLOUDBUILD_SOURCE_RETENTION_DAYS)
    protected = {url for _, url in source_packages[:CLOUDBUILD_SOURCE_KEEP_RECENT]}
    removable = [
        url
        for updated, url in source_packages
        if updated < cutoff and url not in protected
    ]

    if not removable:
        logging.info(
            "Pacotes fonte preservados: %s mais recentes e itens com menos de %s dias.",
            min(len(source_packages), CLOUDBUILD_SOURCE_KEEP_RECENT),
            CLOUDBUILD_SOURCE_RETENTION_DAYS,
        )
        return

    logging.info(
        "Removendo %s pacote(s) fonte antigo(s) fora da janela de retencao.",
        len(removable),
    )
    for url in removable:
        run_cmd(["gcloud", "storage", "rm", url])


def main() -> int:
    logging.info("Verificando armazenamento do Google Cloud...")
    ar_size = get_artifact_registry_size_mb()
    gcs_size = get_cloud_build_bucket_size_mb()
    total_size = ar_size + gcs_size

    logging.info(
        f"Artifact Registry: {ar_size:.2f} MB | Cloud Storage (Build): {gcs_size:.2f} MB"
    )
    logging.info(
        f"Tamanho Total Estimado: {total_size:.2f} MB / Limite Estipulado: {MAX_MB:.2f} MB"
    )

    if total_size >= THRESHOLD_MB:
        logging.warning(
            f"Capacidade em {total_size / MAX_MB * 100:.1f}% (> 85%). Gatilho de Higienizacao ativado!"
        )
        clean_cloud_build_bucket()
        clean_artifact_registry()

        ar_size = get_artifact_registry_size_mb()
        gcs_size = get_cloud_build_bucket_size_mb()
        new_total = ar_size + gcs_size
        logging.info(f"Limpeza concluida. Novo tamanho total: {new_total:.2f} MB")
    else:
        logging.info(
            "Armazenamento seguro (Abaixo de 85%). Nenhuma acao destrutiva necessaria."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
