from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APK_PATH = ROOT / "apps" / "valley-android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
DEFAULT_BUCKET = "all-in-one-public-artifacts"
DEFAULT_OBJECT = "valley-latest.apk"


def find_gcloud() -> str:
    discovered = shutil.which("gcloud")
    if discovered:
        return discovered
    raise RuntimeError("Google Cloud SDK nao encontrado no PATH.")


def run_command(command: list[str], check: bool = True) -> str:
    result = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Erro ao executar comando: {error_msg}")
    return result.stdout.strip()


def deploy_apk(project_id: str, bucket_name: str, object_name: str) -> str:
    gcloud = find_gcloud()

    if not APK_PATH.exists():
        raise FileNotFoundError(f"APK nao encontrado em: {APK_PATH}. Certifique-se de executar o build antes.")

    print(f"[*] Verificando existencia do bucket gs://{bucket_name}...")
    buckets_raw = run_command([gcloud, "storage", "buckets", "list", f"--project={project_id}", "--format=json"])
    buckets = json.loads(buckets_raw) if buckets_raw else []

    bucket_exists = any(b.get("name") == bucket_name for b in buckets)

    if not bucket_exists:
        print(f"[+] Criando bucket gs://{bucket_name} em us-central1...")
        run_command([gcloud, "storage", "buckets", "create", f"gs://{bucket_name}", f"--project={project_id}", "--location=us-central1"])

    print(f"[*] Fazendo upload do APK: {APK_PATH} -> gs://{bucket_name}/{object_name}...")
    run_command([gcloud, "storage", "cp", str(APK_PATH), f"gs://{bucket_name}/{object_name}", f"--project={project_id}"])

    print("[*] Configurando permissao de leitura publica...")
    run_command([
        gcloud, "storage", "buckets", "add-iam-policy-binding", f"gs://{bucket_name}",
        f"--project={project_id}", "--member=allUsers", "--role=roles/storage.objectViewer"
    ])

    public_url = f"https://storage.googleapis.com/{bucket_name}/{object_name}"
    return public_url


def main() -> int:
    parser = argparse.ArgumentParser(description="Realiza o deploy do APK para o Google Cloud Storage e gera link publico.")
    parser.add_argument("--project", help="ID do projeto Google Cloud (opcional se GOOGLE_CLOUD_PROJECT estiver definido)")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET, help=f"Nome do bucket (padrao: {DEFAULT_BUCKET})")
    parser.add_argument("--name", default=DEFAULT_OBJECT, help=f"Nome do objeto no bucket (padrao: {DEFAULT_OBJECT})")

    args = parser.parse_args()
    project_id = args.project or os.getenv("GOOGLE_CLOUD_PROJECT")

    if not project_id:
        print("Erro: ID do projeto nao definido. Use --project ou defina GOOGLE_CLOUD_PROJECT.", file=sys.stderr)
        return 1

    try:
        url = deploy_apk(project_id, args.bucket, args.name)
        print("\n" + "="*50)
        print("✅ DEPLOY CONCLUIDO COM SUCESSO!")
        print(f"🔗 Link para download: {url}")
        print("="*50)
        return 0
    except Exception as e:
        print(f"❌ Falha no deploy: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
