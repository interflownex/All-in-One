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
    # .env.example do projeto ja e compatível com source em bash.
    set -a
    # shellcheck disable=SC1090
    source "$file"
    set +a
  fi
}

refresh_generated_env_files() {
  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT/scripts/configure_docker_dx.py" >/dev/null
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

  load_env_file "$ROOT/.env.example"
  load_env_file "$ROOT/.env"
  refresh_generated_env_files
  load_env_file "$ROOT/.env.docker-dx"
  export_workspace_defaults
  prepare_python

  echo "Ambiente WSL preparado em: $ROOT"
  echo "Variaveis principais carregadas do .env.example, .env e .env.docker-dx, quando existirem."
}

if is_sourced; then
  bootstrap "$@"
else
  bootstrap "$@"
fi
