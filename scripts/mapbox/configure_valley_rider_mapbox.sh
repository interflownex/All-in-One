#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP_DIR="$ROOT_DIR/apps/valley_rider"
OUTPUT_DIR="$ROOT_DIR/tmp/mapbox-secrets"
DEFAULT_STAGING_URL="https://all-in-one-web-7fa.pages.dev"
DEFAULT_PRODUCTION_URL="https://brasildesconto.com.br"

cleanup() {
  unset MAPBOX_ADMIN_TOKEN VITE_MAPBOX_ACCESS_TOKEN || true
}
trap cleanup EXIT

fail() {
  printf '\nERRO: %s\n' "$1" >&2
  exit 1
}

command -v node >/dev/null 2>&1 || fail "Node.js não foi encontrado."
command -v npm >/dev/null 2>&1 || fail "npm não foi encontrado."
[[ -f "$ROOT_DIR/scripts/mapbox/provision_valley_rider_tokens.mjs" ]] || fail "Provisionador Mapbox não encontrado."
[[ -f "$ROOT_DIR/scripts/mapbox/validate_valley_rider_mapbox.mjs" ]] || fail "Validador Mapbox não encontrado."
[[ -d "$APP_DIR" ]] || fail "Aplicativo Valley Rider não encontrado."

printf '\nConfiguração segura Mapbox — Valley Rider\n'
printf 'O token secreto será lido sem aparecer na tela e não será gravado no Git.\n\n'

read -r -p "Usuário da conta Mapbox: " MAPBOX_USERNAME
[[ -n "${MAPBOX_USERNAME// }" ]] || fail "Usuário Mapbox obrigatório."

read -r -s -p "Token temporário Mapbox (sk.): " MAPBOX_ADMIN_TOKEN
printf '\n'
[[ "$MAPBOX_ADMIN_TOKEN" == sk.* ]] || fail "O token administrativo deve começar com sk."

read -r -p "URL de staging [$DEFAULT_STAGING_URL]: " staging_input
MAPBOX_WEB_ALLOWED_URLS_STAGING="${staging_input:-$DEFAULT_STAGING_URL}"

read -r -p "URL de produção [$DEFAULT_PRODUCTION_URL]: " production_input
MAPBOX_WEB_ALLOWED_URLS_PRODUCTION="${production_input:-$DEFAULT_PRODUCTION_URL}"

node -e 'new URL(process.argv[1]); new URL(process.argv[2]);' \
  "$MAPBOX_WEB_ALLOWED_URLS_STAGING" \
  "$MAPBOX_WEB_ALLOWED_URLS_PRODUCTION" \
  || fail "Uma das URLs informadas é inválida."

[[ "$MAPBOX_WEB_ALLOWED_URLS_STAGING" == https://* ]] || fail "Staging deve usar HTTPS."
[[ "$MAPBOX_WEB_ALLOWED_URLS_PRODUCTION" == https://* ]] || fail "Produção deve usar HTTPS."

export MAPBOX_USERNAME MAPBOX_ADMIN_TOKEN
export MAPBOX_ENVIRONMENTS="staging,production"
export MAPBOX_WEB_ALLOWED_URLS_STAGING MAPBOX_WEB_ALLOWED_URLS_PRODUCTION
export MAPBOX_CREATE_MOBILE_TOKENS="true"
export MAPBOX_OUTPUT_DIR="$OUTPUT_DIR"

printf '\n[1/5] Criando tokens separados e restritos...\n'
node "$ROOT_DIR/scripts/mapbox/provision_valley_rider_tokens.mjs"

STAGING_ENV="$OUTPUT_DIR/.env.mapbox.staging.local"
PRODUCTION_ENV="$OUTPUT_DIR/.env.mapbox.production.local"
[[ -f "$STAGING_ENV" ]] || fail "Arquivo de staging não foi gerado."
[[ -f "$PRODUCTION_ENV" ]] || fail "Arquivo de produção não foi gerado."

printf '\n[2/5] Instalando a credencial de staging no aplicativo local...\n'
install -m 600 "$STAGING_ENV" "$APP_DIR/.env.local"

printf '\n[3/5] Instalando dependências reproduzíveis...\n'
(
  cd "$APP_DIR"
  npm ci
)

printf '\n[4/5] Executando lint e build...\n'
(
  cd "$APP_DIR"
  npm run lint
  npm run build
)

printf '\n[5/5] Validando Style, Directions e Geocoding com o token de staging...\n'
set -a
# shellcheck disable=SC1090
source "$STAGING_ENV"
set +a
export MAPBOX_TEST_REFERER="$MAPBOX_WEB_ALLOWED_URLS_STAGING"
node "$ROOT_DIR/scripts/mapbox/validate_valley_rider_mapbox.mjs"
unset VITE_MAPBOX_ACCESS_TOKEN MAPBOX_TEST_REFERER

printf '\nCONFIGURAÇÃO CONCLUÍDA\n'
printf 'Tokens e manifesto: %s\n' "$OUTPUT_DIR"
printf 'Staging local ativo: %s\n' "$APP_DIR/.env.local"
printf 'Produção protegida: %s\n' "$PRODUCTION_ENV"
printf '\nRevogue agora o token temporário sk. no console Mapbox.\n'
printf 'Os quatro tokens definitivos permanecerão separados por ambiente e plataforma.\n'
