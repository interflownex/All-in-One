from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Mapping

SECRET_ENV_BY_ID: Mapping[str, str] = {
    "identity-dsn": "AIO_IDENTITY_DSN",
    "jwt-secret": "AIO_JWT_SECRET",
    "document-encryption-key": "AIO_DOCUMENT_ENCRYPTION_KEY",
}


def _run_quiet(command: list[str], *, input_text: str | None = None) -> int:
    """Executa gcloud sem expor payload, stdout ou stderr nos logs."""

    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("A CLI gcloud não está instalada ou não está no PATH.") from exc
    return result.returncode


def _secret_exists(project_id: str, secret_id: str) -> bool:
    return (
        _run_quiet(
            [
                "gcloud",
                "secrets",
                "describe",
                secret_id,
                "--project",
                project_id,
            ]
        )
        == 0
    )


def _create_secret(project_id: str, secret_id: str) -> None:
    return_code = _run_quiet(
        [
            "gcloud",
            "secrets",
            "create",
            secret_id,
            "--replication-policy=automatic",
            "--project",
            project_id,
        ]
    )
    if return_code != 0:
        raise RuntimeError(
            f"Falha ao criar o segredo '{secret_id}' (código={return_code})."
        )


def _add_secret_version(project_id: str, secret_id: str, payload: str) -> None:
    if not payload:
        raise ValueError(f"Payload vazio para o segredo '{secret_id}'.")

    return_code = _run_quiet(
        [
            "gcloud",
            "secrets",
            "versions",
            "add",
            secret_id,
            "--data-file=-",
            "--project",
            project_id,
        ],
        input_text=payload,
    )
    if return_code != 0:
        raise RuntimeError(
            f"Falha ao adicionar versão ao segredo '{secret_id}' "
            f"(código={return_code})."
        )


def configure_secret(project_id: str, secret_id: str, payload: str) -> None:
    if not _secret_exists(project_id, secret_id):
        _create_secret(project_id, secret_id)
    _add_secret_version(project_id, secret_id, payload)
    print("Segredo configurado com nova versão.")


def _load_configuration() -> tuple[str, dict[str, str]]:
    project_id = os.environ.get("GCP_PROJECT_ID", "").strip()
    missing = ["GCP_PROJECT_ID"] if not project_id else []
    payloads: dict[str, str] = {}

    for secret_id, env_name in SECRET_ENV_BY_ID.items():
        value = os.environ.get(env_name, "")
        if not value:
            missing.append(env_name)
        else:
            payloads[secret_id] = value

    if missing:
        raise ValueError(
            "Variáveis de ambiente obrigatórias ausentes: " + ", ".join(missing)
        )
    return project_id, payloads


def main() -> int:
    try:
        project_id, payloads = _load_configuration()
        print("Iniciando configuração segura no Google Secret Manager.")
        for secret_id, payload in payloads.items():
            configure_secret(project_id, secret_id, payload)
    except (RuntimeError, ValueError):
        # Não propaga texto de exceção para logs: mensagens derivadas de fluxos
        # sensíveis podem ser classificadas como exposição pelo CodeQL.
        print(
            "Falha na configuração segura. Verifique ambiente, permissões e gcloud.",
            file=sys.stderr,
        )
        return 1

    print("Configuração concluída sem exposição de payloads.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
