#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

is_sourced() {
  [[ "${BASH_SOURCE[0]}" != "$0" ]]
}

require_wsl() {
  if ! grep -qi microsoft /proc/version 2>/dev/null; then
    echo "Este bootstrap foi desenhado para WSL." >&2
    return 1
  fi
}

load_env_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ -z "$line" ]] && continue
      [[ "$line" =~ ^[[:space:]]*# ]] && continue
      if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
        local key="${line%%=*}"
        local raw_value="${line#*=}"
        # Remove aspas simples ou duplas completas do valor.
        raw_value="${raw_value%\"}"
        raw_value="${raw_value#\"}"
        raw_value="${raw_value%\'}"
        raw_value="${raw_value#\'}"
        export "$key=$raw_value"
      fi
    done <"$file"
  fi
}

refresh_generated_env_files() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT/scripts/configure_docker_dx.py" >/dev/null
  fi
}

validate_wsl_dns_persistence() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT/scripts/configure_wsl_dns.py" --check >/dev/null
  fi
}

export_workspace_defaults() {
  export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-all-in-one-dx}"
  export DOCKER_BUILDKIT="${DOCKER_BUILDKIT:-1}"
  export COMPOSE_DOCKER_CLI_BUILD="${COMPOSE_DOCKER_CLI_BUILD:-1}"
  export BUILDKIT_PROGRESS="${BUILDKIT_PROGRESS:-plain}"
  export GOOGLE_INTEGRATIONS_ENABLED="${GOOGLE_INTEGRATIONS_ENABLED:-false}"
  export GOOGLE_CLOUD_ENABLED="${GOOGLE_CLOUD_ENABLED:-false}"
  export GOOGLE_AI_STUDIO_ENABLED="${GOOGLE_AI_STUDIO_ENABLED:-false}"
  export GOOGLE_CODE_CLI_ENABLED="${GOOGLE_CODE_CLI_ENABLED:-false}"
  export ALLOYDB_ENABLED="${ALLOYDB_ENABLED:-false}"
  export STITCH_REMOTE_SYNC_ENABLED="${STITCH_REMOTE_SYNC_ENABLED:-false}"
  export GEMINI_CODE_ASSIST_ENABLED="${GEMINI_CODE_ASSIST_ENABLED:-true}"
}

ensure_local_bin_on_path() {
  local local_bin="$HOME/.local/bin"
  mkdir -p "$local_bin"
  case ":$PATH:" in
    *":$local_bin:"*) ;;
    *) export PATH="$PATH:$local_bin" ;;
  esac
}

install_docker_compose_local() {
  if command -v docker-compose >/dev/null 2>&1; then
    return 0
  fi

  local arch
  case "$(uname -m)" in
    x86_64) arch="x86_64" ;;
    aarch64|arm64) arch="aarch64" ;;
    *)
      echo "Arquitetura nao suportada para docker-compose: $(uname -m)" >&2
      return 1
      ;;
  esac

  local compose_url="https://github.com/docker/compose/releases/download/v2.39.3/docker-compose-linux-${arch}"
  curl -fL "$compose_url" -o "$HOME/.local/bin/docker-compose"
  chmod +x "$HOME/.local/bin/docker-compose"
}

install_minikube_local() {
  if command -v minikube >/dev/null 2>&1; then
    return 0
  fi

  local arch
  case "$(uname -m)" in
    x86_64) arch="amd64" ;;
    aarch64|arm64) arch="arm64" ;;
    *)
      echo "Arquitetura nao suportada para minikube: $(uname -m)" >&2
      return 1
      ;;
  esac

  local minikube_url="https://storage.googleapis.com/minikube/releases/latest/minikube-linux-${arch}"
  curl -fL "$minikube_url" -o "$HOME/.local/bin/minikube"
  chmod +x "$HOME/.local/bin/minikube"
}

configure_minikube_non_blocking_updates() {
  export MINIKUBE_WANTUPDATENOTIFICATION="false"
  if command -v minikube >/dev/null 2>&1; then
    minikube config set WantUpdateNotification false >/dev/null 2>&1 || true
    minikube config set WantReportErrorPrompt false >/dev/null 2>&1 || true
  fi
}

verify_local_toolchain() {
  command -v docker >/dev/null 2>&1 || {
    echo "docker nao encontrado no PATH." >&2
    return 1
  }
  command -v kubectl >/dev/null 2>&1 || {
    echo "kubectl nao encontrado no PATH." >&2
    return 1
  }
  command -v helm >/dev/null 2>&1 || {
    echo "helm nao encontrado no PATH." >&2
    return 1
  }
  command -v docker-compose >/dev/null 2>&1 || {
    echo "docker-compose nao encontrado no PATH." >&2
    return 1
  }
  command -v minikube >/dev/null 2>&1 || {
    echo "minikube nao encontrado no PATH." >&2
    return 1
  }
}

prepare_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 nao encontrado no WSL." >&2
    return 1
  fi

  if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
    python3 -m venv "$ROOT/.venv"
  fi

  # Mantem o ambiente local isolado e fiel ao workspace.
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
  python -m pip install --upgrade pip
  python -m pip install -r "$ROOT/requirements-dev.txt"
}

bootstrap() {
  require_wsl
  cd "$ROOT"

  ensure_local_bin_on_path

  load_env_file "$ROOT/.env.example"
  load_env_file "$ROOT/.env"
  refresh_generated_env_files
  validate_wsl_dns_persistence
  load_env_file "$ROOT/.env.docker-dx"
  export_workspace_defaults
  install_docker_compose_local
  install_minikube_local
  configure_minikube_non_blocking_updates
  verify_local_toolchain
  prepare_python

  echo "Ambiente WSL preparado em: $ROOT"
  echo "Variaveis principais carregadas do .env.example, .env e .env.docker-dx, quando existirem."
  echo "Toolchain ativa: docker, docker-compose, kubectl, helm e minikube."
}

if is_sourced; then
  bootstrap "$@"
else
  bootstrap "$@"
fi
