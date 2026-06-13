# Provisionamento Autonomo do All-in-One no WSL

## Instrucao mandataria para o Codex

Este documento e uma ordem de execucao para o Codex operando dentro de uma
distribuicao WSL. O Codex deve executar, corrigir e validar todas as etapas, em
vez de apenas explicar comandos.

Todo o ambiente de desenvolvimento deve ficar no WSL:

```text
/home/eretazan/all-in-one
```

O Windows deve atuar somente como host obrigatorio do WSL 2 e do WSLg. Nenhum
aplicativo, editor, CLI, SDK, runtime, daemon, extensao ou configuracao de
desenvolvimento deve ser instalado no ambiente Windows.

Antigravity IDE para Linux, Antigravity CLI, Git, GitHub CLI, Python, Node.js,
Java, Docker Engine, Docker Compose, Terraform, kubectl, Helm, dependencias,
bancos, filas, testes, builds, APK, extensoes e servidores MCP devem ser
instalados e executados dentro do WSL.

So e permitido interromper quando uma autenticacao humana for inevitavel ou um
recurso externo estiver comprovadamente indisponivel.

## Objetivo

Substituir integralmente a base WSL existente:

```text
/home/eretazan/all-in-one
```

por um clone limpo de:

```text
Repositorio: https://github.com/interflownex/All-in-One.git
Branch: main
Referencia autoritativa: origin/main
```

O ambiente final deve ser local-first e funcionar sem Cloud Shell, Cloud Build,
Cloud Run, GKE, AlloyDB, ADC, projeto Google Cloud ou billing Google.

## Regras inegociaveis

1. `origin/main` e a fonte de verdade.
2. A base antiga nao pode ser mesclada ou reaplicada no clone novo.
3. Antes da substituicao, criar backup datado fora do diretorio alvo.
4. Nunca copiar `.env`, tokens, chaves ou credenciais do backup.
5. Nunca executar `git reset --hard` na base antiga.
6. Nao apagar o backup automaticamente.
7. Nao desenvolver em `/mnt/c`, `/mnt/d` ou outro filesystem montado do
   Windows. O repositorio deve permanecer no filesystem Linux do WSL.
8. Nao instalar Antigravity, Docker Desktop ou qualquer toolchain no Windows.
9. Preservar `AGENTS.md`, `GEMINI.md` e politicas recebidas de `origin/main`.
10. Depois do clone, trabalhos futuros devem usar branch `codex/<descricao>`.
11. Segredos nunca devem ser escritos em arquivos versionados ou no JSON MCP.
12. Integracoes Google devem permanecer desativadas e nao podem bloquear o
    ambiente local.

## Estado final esperado

- clone limpo em `/home/eretazan/all-in-one`;
- backup datado em `/home/eretazan/backups`;
- usuario Linux efetivo `eretazan`;
- Python usando `/home/eretazan/all-in-one/.venv/bin/python`;
- Node.js na versao definida em `.nvmrc`;
- Docker Engine e Compose executando dentro do WSL;
- Antigravity Linux instalado e executando dentro do WSL por WSLg;
- MCPs iniciados dentro do WSL;
- testes, builds web, Compose e APK validados;
- nenhuma dependencia operacional do Google Cloud.

## Fase 1 - Entrar e validar o WSL

O unico preflight permitido fora do Linux e verificar se a plataforma WSL 2
com WSLg ja existe. Esses comandos nao instalam ferramentas de desenvolvimento
no Windows:

```powershell
wsl --status
wsl --list --verbose
```

Se o WSL nao estiver instalado:

```powershell
wsl --install -d Ubuntu
```

Reiniciar o Windows somente quando exigido e continuar automaticamente depois.
Todos os comandos seguintes devem executar dentro do WSL, como `eretazan`.

```powershell
wsl -d Ubuntu -u eretazan
```

Dentro do WSL:

```bash
set -Eeuo pipefail

test "$(id -un)" = "eretazan"
test "$HOME" = "/home/eretazan"
grep -qi microsoft /proc/version

export TARGET="/home/eretazan/all-in-one"
export PARENT="/home/eretazan"
export BACKUP_ROOT="/home/eretazan/backups"
export TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
export BACKUP="$BACKUP_ROOT/all-in-one-before-cloud-$TIMESTAMP"
export INVENTORY="$BACKUP_ROOT/all-in-one-inventory-$TIMESTAMP.txt"
export REPOSITORY="https://github.com/interflownex/All-in-One.git"
export BRANCH="main"

mkdir -p "$PARENT" "$BACKUP_ROOT"
```

Se o usuario `eretazan` ou a distribuicao escolhida nao existir, o Codex deve
identificar a distribuicao Ubuntu instalada, criar o usuario com `adduser`,
conceder `sudo` e definir esse usuario como padrao antes de continuar.

## Fase 2 - Inventario, backup e clone limpo

Registrar o estado antigo:

```bash
if [[ -e "$TARGET" ]]; then
  {
    printf 'Data UTC: %s\n' "$(date -u +%FT%TZ)"
    printf 'Origem local: %s\n' "$TARGET"
    printf 'Destino do backup: %s\n' "$BACKUP"

    if [[ -d "$TARGET/.git" ]]; then
      git -C "$TARGET" status --short --branch || true
      git -C "$TARGET" log -1 --format='%H %cI %s' || true
      git -C "$TARGET" remote -v || true
    fi
  } >"$INVENTORY"
fi
```

Sair do diretorio, mover a base antiga e clonar:

```bash
cd "$PARENT"

if [[ -e "$TARGET" ]]; then
  mv -- "$TARGET" "$BACKUP"
fi

restore_previous_workspace() {
  rm -rf -- "$TARGET"
  if [[ -e "$BACKUP" ]]; then
    mv -- "$BACKUP" "$TARGET"
  fi
}

if ! git clone \
  --branch "$BRANCH" \
  --single-branch \
  --origin origin \
  "$REPOSITORY" \
  "$TARGET"; then
  restore_previous_workspace
  printf 'Clone remoto falhou; a base anterior foi restaurada.\n' >&2
  exit 1
fi

cd "$TARGET"
git fetch --prune origin
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")"
test -z "$(git status --porcelain)"
```

O backup deve permanecer em `/home/eretazan/backups`. Nao copiar arquivos dele
para o clone novo.

## Fase 3 - Atualizar o WSL e instalar ferramentas

Instalar pacotes Linux:

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  unzip \
  zip \
  python3.12 \
  python3.12-venv \
  python3-pip \
  openjdk-17-jdk \
  postgresql-client \
  shellcheck \
  sqlite3
```

Se `python3.12` nao estiver no repositorio da distribuicao, instalar a versao
3.12 por um repositorio Ubuntu confiavel ou `pyenv`, sem substituir o Python
usado internamente pelo sistema.

### GitHub CLI

Instalar pelo repositorio oficial:

```bash
if ! command -v gh >/dev/null 2>&1; then
  sudo install -d -m 0755 /etc/apt/keyrings
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg |
    sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
  sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" |
    sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
  sudo apt-get update
  sudo apt-get install -y gh
fi
```

### Node.js

Instalar `fnm` no usuario WSL:

```bash
if ! command -v fnm >/dev/null 2>&1; then
  curl -fsSL https://fnm.vercel.app/install | bash
fi

export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(fnm env --shell bash)"

NODE_VERSION="$(tr -d '[:space:]v' <"$TARGET/.nvmrc")"
fnm install "$NODE_VERSION"
fnm use "$NODE_VERSION"
fnm default "$NODE_VERSION"
```

Garantir no `~/.bashrc`, sem duplicacao:

```bash
grep -Fq 'fnm env --shell bash' "$HOME/.bashrc" ||
  printf '\neval "$(fnm env --use-on-cd --shell bash)"\n' >>"$HOME/.bashrc"
```

### Terraform, kubectl e Helm

Instalar somente a partir dos repositorios oficiais. O Codex deve validar a
assinatura ou keyring de cada repositorio e entao instalar:

```text
terraform
kubectl
helm
```

Nao instalar `gcloud`.

### Verificacoes

```bash
git --version
gh --version
python3.12 --version
node --version
npm --version
java -version
terraform version
kubectl version --client
helm version
```

## Fase 4 - Docker Engine nativo no WSL

Nao depender do Docker Desktop para o runtime. Instalar o Docker Engine e o
plugin Compose dentro do WSL pelo repositorio oficial Docker:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg |
  sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

. /etc/os-release
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo usermod -aG docker eretazan
```

Ativar `systemd` no WSL:

```bash
if [[ ! -f /etc/wsl.conf ]] ||
   ! grep -Eq '^\s*systemd\s*=\s*true\s*$' /etc/wsl.conf; then
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true

[user]
default=eretazan
EOF
fi
```

Quando `/etc/wsl.conf` mudar, executar no Windows:

```powershell
wsl --shutdown
```

Reabrir o WSL e continuar:

```bash
sudo systemctl enable --now docker
docker version
docker compose version
docker run --rm hello-world
```

Se o grupo `docker` ainda nao estiver aplicado, iniciar uma nova sessao WSL.
Nao usar `chmod 666 /var/run/docker.sock`.

## Fase 5 - Antigravity Linux dentro do WSL

Nao instalar nem usar a versao Windows do Antigravity. Instalar a versao Linux
oficial diretamente no Ubuntu WSL pelo repositorio APT publicado em:

```text
https://antigravity.google/download/linux
```

Executar dentro do WSL:

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg |
  sudo gpg --dearmor --yes \
    -o /etc/apt/keyrings/antigravity-repo-key.gpg

echo \
  "deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main" |
  sudo tee /etc/apt/sources.list.d/antigravity.list >/dev/null

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y antigravity
```

Confirmar que o pacote e o executavel sao Linux:

```bash
dpkg-query -W -f='${Package} ${Version}\n' antigravity
command -v antigravity
file "$(command -v antigravity)"
antigravity --version
```

O caminho retornado por `command -v` deve estar no filesystem Linux e `file`
deve identificar um executavel ou launcher Linux. Nao aceitar um `.exe` vindo
do `PATH` interoperavel do Windows.

### Validar WSLg

O Antigravity grafico deve executar pelo WSLg. Verificar:

```bash
test -n "${WAYLAND_DISPLAY:-}"
test -n "${DISPLAY:-}"
test -d /mnt/wslg
test -S "/mnt/wslg/runtime-dir/${WAYLAND_DISPLAY}" ||
  test -S /tmp/.X11-unix/X0
```

Se WSLg estiver ausente, atualizar a plataforma WSL com `wsl --update` e
reiniciar o WSL com `wsl --shutdown`. Isso e manutencao da plataforma WSL, nao
instalacao do Antigravity no Windows.

Instalar bibliotecas Linux comuns exigidas por aplicativos Electron/Chromium:

```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  dbus-x11 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libcups2 \
  libdrm2 \
  libgbm1 \
  libgles2 \
  libgtk-3-0 \
  libnss3 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxkbcommon0 \
  libxrandr2 \
  xdg-utils

if apt-cache show libasound2t64 >/dev/null 2>&1; then
  sudo apt-get install -y libasound2t64
else
  sudo apt-get install -y libasound2
fi
```

Iniciar o Antigravity Linux dentro do WSL:

```bash
cd /home/eretazan/all-in-one
mkdir -p "$HOME/.local/state"
nohup antigravity /home/eretazan/all-in-one \
  >"$HOME/.local/state/antigravity.log" 2>&1 &
```

Se houver falha de aceleracao grafica, repetir somente para diagnostico com:

```bash
antigravity --disable-gpu /home/eretazan/all-in-one
```

Nao substituir o Antigravity Linux por uma instalacao Windows.

O terminal integrado do Antigravity deve retornar:

```bash
pwd
whoami
uname -a
```

Resultados obrigatorios:

```text
/home/eretazan/all-in-one
eretazan
Linux ... microsoft ...
```

Validar que o processo do editor esta no WSL:

```bash
pgrep -a -f 'antigravity'
readlink -f "/proc/$(pgrep -o -f antigravity)/exe"
```

O executavel resolvido deve ser Linux e nao pode apontar para `/mnt/c`.

## Fase 6 - Python e Playwright

```bash
cd "$TARGET"
rm -rf .venv
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt

find modules workers -type f -name requirements.txt -print0 |
  while IFS= read -r -d '' requirements; do
    .venv/bin/python -m pip install -r "$requirements"
  done

.venv/bin/python -m playwright install --with-deps chromium
```

O interpretador do Antigravity deve ser:

```text
/home/eretazan/all-in-one/.venv/bin/python
```

## Fase 7 - Dependencias web

```bash
cd "$TARGET"

APPLICATIONS=(
  apps/all-in-one
  apps/all-in-one-business
  apps/valley
  apps/valley_business
  apps/valley_rider
  desktop/valley-erp
)

for application in "${APPLICATIONS[@]}"; do
  if [[ -f "$application/package.json" ]]; then
    if [[ -f "$application/package-lock.json" ]]; then
      npm --prefix "$application" ci
    else
      npm --prefix "$application" install
    fi
  fi
done
```

## Fase 8 - Configuracao local sem Google

```bash
cd "$TARGET"
[[ -f .env ]] || cp .env.example .env

ENCRYPTION_KEY="$(
  .venv/bin/python -c \
    'import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'
)"

.venv/bin/python - "$ENCRYPTION_KEY" <<'PY'
from pathlib import Path
import re
import sys

path = Path(".env")
content = path.read_text(encoding="utf-8")
key = sys.argv[1]
name = "ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY"
pattern = rf"(?m)^{re.escape(name)}=.*$"
line = f"{name}={key}"
content = re.sub(pattern, line, content) if re.search(pattern, content) else content + "\n" + line + "\n"
path.write_text(content, encoding="utf-8")
PY
```

Garantir no `.env` local:

```dotenv
POSTGRES_DB=all_in_one
POSTGRES_USER=all_in_one
POSTGRES_PASSWORD=local-development-only
MONGO_INITDB_DATABASE=all_in_one
RABBITMQ_DEFAULT_USER=all_in_one
RABBITMQ_DEFAULT_PASS=local-development-only
GOOGLE_INTEGRATIONS_ENABLED=false
GOOGLE_CLOUD_ENABLED=false
GOOGLE_AI_STUDIO_ENABLED=false
GOOGLE_CODE_CLI_ENABLED=false
ALLOYDB_ENABLED=false
ALLOYDB_DSN=
GEMINI_CODE_ASSIST_ENABLED=false
STITCH_REMOTE_SYNC_ENABLED=false
```

Validar:

```bash
git check-ignore .env
```

## Fase 9 - Extensoes no contexto WSL

Instalar as extensoes na unica instancia existente, o Antigravity Linux:

```text
ms-python.python
ms-python.vscode-pylance
ms-python.debugpy
charliermarsh.ruff
ms-azuretools.vscode-docker
redhat.vscode-yaml
esbenp.prettier-vscode
dbaeumer.vscode-eslint
github.vscode-github-actions
github.vscode-pull-request-github
eamodio.gitlens
ms-kubernetes-tools.vscode-kubernetes-tools
hashicorp.terraform
vscjava.vscode-java-pack
vscjava.vscode-gradle
fwcd.kotlin
humao.rest-client
editorconfig.editorconfig
```

`GoogleCloudTools.datacloud` nao e obrigatoria no perfil WSL local-first. Nao
instalar a extensao nem qualquer dependencia dela no Windows.

## Fase 10 - Servidores MCP dentro do WSL

Usar a configuracao Linux:

```text
/home/eretazan/.gemini/config/mcp_config.json
```

Nao usar `C:\Users\...\mcp_config.json` como configuracao autoritativa deste
workspace.

Instalar os servidores Node:

```bash
npm install --global \
  @playwright/mcp \
  @modelcontextprotocol/server-filesystem
```

Criar backup e fazer merge estruturado do JSON:

```bash
export MCP_DIRECTORY="/home/eretazan/.gemini/config"
export MCP_CONFIG="$MCP_DIRECTORY/mcp_config.json"
mkdir -p "$MCP_DIRECTORY"

if [[ -f "$MCP_CONFIG" ]]; then
  cp -- "$MCP_CONFIG" \
    "$MCP_DIRECTORY/mcp_config.before-all-in-one-$TIMESTAMP.json"
fi

.venv/bin/python - "$MCP_CONFIG" "$TARGET" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
workspace = str(Path(sys.argv[2]).resolve())

if config_path.exists():
    data = json.loads(config_path.read_text(encoding="utf-8"))
else:
    data = {}

servers = data.setdefault("mcpServers", {})
servers["filesystem-all-in-one"] = {
    "command": "npx",
    "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        workspace,
    ],
}
servers["playwright"] = {
    "command": "npx",
    "args": ["-y", "@playwright/mcp@latest", "--headless"],
}
servers["context7"] = {
    "serverUrl": "https://mcp.context7.com/mcp",
}

config_path.write_text(
    json.dumps(data, ensure_ascii=True, indent=2) + "\n",
    encoding="utf-8",
)
PY

jq empty "$MCP_CONFIG"
```

O MCP filesystem deve acessar somente `/home/eretazan/all-in-one`. Nao
conceder acesso a `/home/eretazan`, `~/.ssh`, `~/.config`, `~/.gemini` ou
backups.

### Docker MCP Gateway

Quando `docker mcp` estiver disponivel no Docker Engine instalado:

```bash
docker mcp --help
MCP_PROFILE="all-in-one-local"
docker mcp profile list | grep -Fq "$MCP_PROFILE" ||
  docker mcp profile create --name "$MCP_PROFILE"
```

Consultar o catalogo e adicionar somente servidores existentes:

```bash
docker mcp catalog server ls mcp/docker-mcp-catalog
```

Priorizar:

```text
playwright
github-official
terraform
filesystem
```

Adicionar o Gateway ao mesmo `mcp_config.json` somente se `docker mcp` existir:

```json
{
  "command": "docker",
  "args": ["mcp", "gateway", "run", "--profile", "all-in-one-local"]
}
```

O nome da entrada deve ser `docker`.

Se a distribuicao do Docker Engine nao fornecer `docker mcp`, manter os MCPs
filesystem, Playwright, Context7 e Terraform independentes. A ausencia do
Toolkit nao deve levar a instalacao do Docker Desktop nem bloquear o runtime.

### Terraform MCP

Instalar o Terraform MCP Server somente de uma release oficial HashiCorp.
Configurar em modo de documentacao ou leitura. Nunca autorizar `terraform
apply`, `destroy`, HCP Terraform ou Terraform Enterprise sem ordem separada.

### MCPs SaaS

Cloudflare, GitHub, Figma e Linear podem ser cadastrados somente por OAuth ou
variaveis de ambiente. Tokens nao devem aparecer no JSON.

Os MCPs `stitch`, `cloudrun` e `gke-oss` devem ficar desativados neste perfil.
Ausencia de credencial deve ser registrada como `desativado sem credencial`.

### Validacao MCP

Reabrir o workspace WSL e atualizar a lista de MCPs. Validar:

- `filesystem-all-in-one` lista somente o workspace;
- `playwright` abre um endpoint local;
- `context7` consulta documentacao publica;
- `terraform` consulta documentacao sem aplicar infraestrutura;
- `docker`, quando disponivel, lista apenas o daemon Docker do WSL.

Todos os processos MCP locais devem aparecer executando no WSL:

```bash
ps -ef | grep -E 'mcp|playwright|filesystem' | grep -v grep
```

## Fase 11 - Acesso externo seguro por OpenSSH e Tailscale

O projeto nao deve ser exposto diretamente na internet. Nao criar port
forwarding no roteador, regra publica de firewall, tunnel HTTP publico ou senha
SSH. O acesso remoto deve ocorrer exclusivamente pela tailnet.

### Instalar e blindar OpenSSH no WSL

```bash
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-server
sudo install -d -m 0755 /etc/ssh/sshd_config.d

sudo tee /etc/ssh/sshd_config.d/60-all-in-one.conf >/dev/null <<'EOF'
Port 22
AddressFamily any
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
AllowUsers eretazan
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding local
PermitTunnel no
GatewayPorts no
ClientAliveInterval 120
ClientAliveCountMax 2
MaxAuthTries 3
LogLevel VERBOSE
EOF

sudo sshd -t
sudo systemctl enable --now ssh
systemctl --no-pager --full status ssh
ss -lntp | grep ':22'
```

O OpenSSH gera automaticamente as chaves de host no WSL. Registrar somente as
chaves publicas e fingerprints:

```bash
sudo ssh-keygen -A
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
sudo cat /etc/ssh/ssh_host_ed25519_key.pub
```

Nunca copiar ou transmitir `/etc/ssh/ssh_host_*_key`.

### Instalar Tailscale no WSL

Instalar a partir do canal oficial Linux:

```bash
curl -fsSL https://tailscale.com/install.sh -o /tmp/install-tailscale.sh
sh -n /tmp/install-tailscale.sh
sudo sh /tmp/install-tailscale.sh
rm -f /tmp/install-tailscale.sh

sudo systemctl enable --now tailscaled
systemctl --no-pager --full status tailscaled
```

Autenticar sem gravar auth key em arquivos ou historico:

```bash
sudo tailscale up \
  --hostname=all-in-one-wsl \
  --accept-dns=true
```

Esse comando pode emitir uma URL de login. O Codex deve aguardar a autenticacao
interativa e continuar. Nao criar, solicitar por Telegram ou persistir uma
Tailscale auth key.

Validar:

```bash
tailscale status
tailscale ip -4
tailscale netcheck
tailscale ping all-in-one-wsl || true
```

Guardar:

```bash
export WSL_TAILSCALE_IP="$(tailscale ip -4)"
export WSL_TAILSCALE_NAME="$(
  tailscale status --json |
    jq -r '.Self.DNSName // .Self.HostName' |
    sed 's/\.$//'
)"
```

Restringir o `sshd` ao loopback e ao IP privado da tailnet:

```bash
sudo tee /etc/ssh/sshd_config.d/70-tailscale-listen.conf >/dev/null <<EOF
ListenAddress 127.0.0.1
ListenAddress ${WSL_TAILSCALE_IP}
EOF

sudo sshd -t
sudo systemctl restart ssh
ss -lntp | grep ':22'
```

O resultado nao pode conter `0.0.0.0:22` nem `[::]:22`. Se o IP Tailscale
mudar, o Codex deve regenerar esse arquivo e reiniciar o `ssh` antes de declarar
o acesso remoto operacional.

O ACL da tailnet deve permitir somente o dispositivo ou usuario do celular para
o destino `all-in-one-wsl:22`. Este perfil usa OpenSSH com chave publica sobre
o transporte WireGuard do Tailscale. Nao habilitar Tailscale SSH na mesma porta
durante esse fluxo, pois ele pode interceptar a conexao destinada ao `sshd`.
Nao usar uma regra global permanente para qualquer origem quando a tailnet
possuir outros membros.

### Preparar Android, Termux e Ubuntu proot

No celular:

1. instalar o Tailscale oficial para Android;
2. entrar na mesma tailnet;
3. instalar Termux por uma fonte oficial suportada pelo projeto;
4. desativar a otimizacao de bateria para Tailscale e Termux;
5. instalar Ubuntu no Termux somente se desejado para o shell de trabalho.

O Tailscale Android deve fornecer a interface VPN do dispositivo. Um Ubuntu
executado por `proot` no Termux nao possui acesso normal ao dispositivo TUN e
nao deve ser tratado como daemon VPN completo.

No Termux:

```bash
pkg update
pkg install openssh jq
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

ssh-keygen \
  -t ed25519 \
  -a 100 \
  -f "$HOME/.ssh/id_ed25519_all_in_one_wsl" \
  -C "termux-all-in-one-wsl"
```

A chave privada deve permanecer exclusivamente no celular:

```text
$HOME/.ssh/id_ed25519_all_in_one_wsl
```

Exibir somente a chave publica:

```bash
cat "$HOME/.ssh/id_ed25519_all_in_one_wsl.pub"
ssh-keygen -lf "$HOME/.ssh/id_ed25519_all_in_one_wsl.pub"
```

Adicionar essa chave publica no WSL por console local ou por um canal confiavel:

```bash
install -d -m 0700 /home/eretazan/.ssh
touch /home/eretazan/.ssh/authorized_keys
chmod 0600 /home/eretazan/.ssh/authorized_keys
```

O Codex deve validar que a linha recebida:

- comeca com `ssh-ed25519`;
- possui comentario `termux-all-in-one-wsl`;
- nao existe ainda em `authorized_keys`;
- e uma chave publica, nunca um arquivo privado.

Depois, anexar a linha integral a:

```text
/home/eretazan/.ssh/authorized_keys
```

e corrigir ownership:

```bash
sudo chown -R eretazan:eretazan /home/eretazan/.ssh
```

No Termux, criar:

```text
$HOME/.ssh/config
```

com:

```sshconfig
Host all-in-one-wsl
    HostName <IP_OU_MAGICDNS_TAILSCALE_DO_WSL>
    User eretazan
    Port 22
    IdentityFile ~/.ssh/id_ed25519_all_in_one_wsl
    IdentitiesOnly yes
    StrictHostKeyChecking yes
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

Para acessar uma aplicacao local sem publica-la:

```bash
ssh -L 8100:127.0.0.1:8100 all-in-one-wsl
```

No navegador do celular, abrir `http://127.0.0.1:8100`. `GatewayPorts no`
impede que esse encaminhamento seja exposto a outros dispositivos.

Cadastrar a chave de host somente depois de comparar o fingerprint exibido no
WSL:

```bash
ssh-keyscan -t ed25519 <IP_OU_MAGICDNS_TAILSCALE_DO_WSL> |
  tee "$HOME/.ssh/all-in-one-wsl.hostkey"
ssh-keygen -lf "$HOME/.ssh/all-in-one-wsl.hostkey"
```

Se o fingerprint corresponder exatamente:

```bash
cat "$HOME/.ssh/all-in-one-wsl.hostkey" >>"$HOME/.ssh/known_hosts"
chmod 600 "$HOME/.ssh/config" "$HOME/.ssh/known_hosts"
ssh all-in-one-wsl
```

Dentro do Ubuntu proot no Termux, montar ou copiar somente a configuracao e a
chave privada a partir do armazenamento privado do Termux, preservando modo
`0600`. Nao colocar chaves em `/sdcard`, Downloads, armazenamento compartilhado
ou backup de nuvem.

### Modo avancado: Tailscale userspace no Ubuntu do Termux

Somente quando o aplicativo Tailscale Android nao puder ser usado, o Codex pode
instalar o binario Linux oficial no Ubuntu proot e iniciar:

```bash
mkdir -p "$HOME/.local/state/tailscale"
tailscaled \
  --tun=userspace-networking \
  --state="$HOME/.local/state/tailscale/tailscaled.state" \
  --socket="$HOME/.local/state/tailscale/tailscaled.sock"
```

Esse modo nao cria uma VPN transparente para todos os processos. Ele exige
proxy SOCKS5/HTTP ou comandos compativeis com o socket userspace e nao substitui
o aplicativo Android para uso geral. Nao executar `tailscaled` root dentro de
um proot esperando acesso ao TUN.

### Encaminhar o manual ao Telegram sem segredos

Telegram pode receber:

- manual completo de conexao;
- IP Tailscale e nome MagicDNS do WSL;
- chave publica do cliente;
- chave publica e fingerprint do host SSH;
- estado dos servicos e comandos de teste.

Telegram nunca pode receber:

- chave privada SSH do celular ou do host;
- senha, recovery code ou seed;
- token do bot Telegram;
- Tailscale auth key, API key ou cookie;
- `.env`, credenciais GitHub ou credenciais Google.

Gerar um relatorio sem segredos:

```bash
export ACCESS_REPORT="$HOME/all-in-one-access-report-$TIMESTAMP.md"
HOST_FINGERPRINT="$(
  sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
)"
TERMUX_PUBLIC_KEY="$(
  grep 'termux-all-in-one-wsl' /home/eretazan/.ssh/authorized_keys |
    tail -n 1
)"

cat >"$ACCESS_REPORT" <<EOF
# Acesso remoto ao All-in-One

- Workspace: /home/eretazan/all-in-one
- Usuario SSH: eretazan
- Destino Tailscale: ${WSL_TAILSCALE_NAME}
- IP Tailscale: ${WSL_TAILSCALE_IP}
- Porta SSH: 22, acessivel somente pela tailnet
- Fingerprint SSH do host: ${HOST_FINGERPRINT}
- Chave publica autorizada do Termux: ${TERMUX_PUBLIC_KEY}

## Termux

1. Ative o Tailscale Android na mesma tailnet.
2. Confirme o fingerprint acima.
3. Execute: ssh all-in-one-wsl

## Regras de seguranca

- A chave privada permanece somente no armazenamento privado do Termux.
- PasswordAuthentication e PermitRootLogin estao desativados.
- Nao existe port forwarding publico para a porta 22.
EOF

chmod 600 "$ACCESS_REPORT"
```

Para enviar, o operador deve fornecer temporariamente ao processo:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Sem gravar esses valores no arquivo, shell history ou repositorio:

```bash
read -rsp 'Telegram bot token: ' TELEGRAM_BOT_TOKEN
printf '\n'
read -rp 'Telegram chat ID: ' TELEGRAM_CHAT_ID
export TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID

curl --fail --silent --show-error \
  -F "chat_id=$TELEGRAM_CHAT_ID" \
  -F "document=@$ACCESS_REPORT" \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument"

unset TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID
```

O envio deve falhar de forma segura quando essas duas variaveis nao forem
fornecidas. Nesse caso, registrar o caminho do relatorio para envio posterior.
Nao contornar a ausencia das credenciais procurando tokens no disco.

## Fase 12 - GitHub

```bash
gh auth status
```

Se necessario:

```bash
gh auth login --web
```

O fluxo de autenticacao deve ser iniciado pelo `gh` do WSL. A credencial deve
ser armazenada no WSL e nunca copiada manualmente para o repositorio.

## Fase 13 - Docker Compose e servicos

```bash
cd "$TARGET"
docker compose -f infra/docker/docker-compose.yml config --quiet
docker compose -f infra/docker/docker-compose.yml up --build -d
docker compose -f infra/docker/docker-compose.yml ps
docker compose -f infra/docker/docker-compose.yml logs --tail 200
```

Investigar e corrigir containers `unhealthy`, `exited` ou reiniciando.

## Fase 14 - Validacoes

```bash
cd "$TARGET"
.venv/bin/python scripts/scaffold_modules.py --check
.venv/bin/python scripts/validate_repository.py
.venv/bin/python -m pytest -q --ignore=tests/e2e
```

Executar E2E somente depois das dependencias web e Chromium:

```bash
.venv/bin/python -m pytest -q tests/e2e
```

Validar healthchecks:

```bash
for endpoint in \
  http://localhost:8100/health \
  http://localhost:8101/health \
  http://localhost:8102/health \
  http://localhost:8112/health \
  http://localhost:8113/health; do
  curl --fail --silent --show-error --max-time 15 "$endpoint" >/dev/null
done
```

Validar builds web:

```bash
for application in "${APPLICATIONS[@]}"; do
  if [[ -f "$application/package.json" ]]; then
    npm --prefix "$application" run build
  fi
done
```

## Fase 15 - Gerar APK no WSL

```bash
cd "$TARGET"
docker build \
  -t all-in-one-android-builder \
  -f infra/docker/android-builder.Dockerfile \
  .

docker run --rm \
  -v "$TARGET:/workspace" \
  -w /workspace/apps/valley-android \
  all-in-one-android-builder \
  bash ./gradlew --no-daemon assembleDebug
```

Validar:

```bash
APK="$TARGET/apps/valley-android/app/build/outputs/apk/debug/app-debug.apk"
test -f "$APK"
sha256sum "$APK"
stat "$APK"
```

O APK nao deve ser commitado. Para acessa-lo pelo Windows:

```text
\\wsl$\Ubuntu\home\eretazan\all-in-one\apps\valley-android\app\build\outputs\apk\debug\app-debug.apk
```

Se a distribuicao tiver outro nome, substituir `Ubuntu` no caminho UNC.

## Fase 16 - Higiene e branch

```bash
cd "$TARGET"
git status --short --branch
git diff --check

WORK_BRANCH="codex/ambiente-local-wsl"
if git show-ref --verify --quiet "refs/heads/$WORK_BRANCH"; then
  git switch "$WORK_BRANCH"
else
  git switch -c "$WORK_BRANCH"
fi
```

Nao criar commit apenas por instalar dependencias, criar `.env` ou gerar
artefatos ignorados.

## Criterios de sucesso

- [ ] workspace em `/home/eretazan/all-in-one`;
- [ ] backup datado em `/home/eretazan/backups`;
- [ ] `HEAD` igual a `origin/main` imediatamente apos o clone;
- [ ] nenhum arquivo antigo reaplicado;
- [ ] desenvolvimento ocorre no filesystem Linux, nao em `/mnt/c`;
- [ ] Python 3.12 e `.venv/bin/python` funcionais;
- [ ] Node.js corresponde a `.nvmrc`;
- [ ] Java 17, Terraform, kubectl e Helm disponiveis no WSL;
- [ ] Docker Engine e Compose executando dentro do WSL;
- [ ] dependencias Python e web instaladas;
- [ ] Compose, validadores, testes unitarios e E2E executados;
- [ ] healthchecks retornam HTTP 200;
- [ ] APK gerado dentro do workspace WSL;
- [ ] pacote Linux do Antigravity foi instalado no WSL;
- [ ] processo grafico do Antigravity executa dentro do WSL por WSLg;
- [ ] nenhuma instalacao Windows do Antigravity foi criada ou utilizada;
- [ ] extensoes foram instaladas no Antigravity Linux;
- [ ] MCPs locais executam dentro do WSL;
- [ ] MCP filesystem esta restrito ao workspace;
- [ ] MCPs Google estao desativados;
- [ ] OpenSSH esta ativo, sem senha e sem login root;
- [ ] porta 22 nao foi publicada na internet;
- [ ] Tailscale e `tailscaled` executam dentro do WSL;
- [ ] celular acessa o WSL pela tailnet;
- [ ] chave privada SSH permanece exclusivamente no Termux;
- [ ] manual sem segredos foi gerado e enviado ao Telegram ou ficou pendente
      somente por ausencia das credenciais do bot;
- [ ] runtime funciona sem Google Cloud, ADC ou AlloyDB;
- [ ] nenhuma credencial foi exposta;
- [ ] backup antigo permanece preservado.

## Relatorio final obrigatorio

Responder em portugues do Brasil com:

1. distribuicao WSL e usuario;
2. caminho do clone;
3. caminho do backup;
4. commit remoto usado;
5. versoes de Python, Node.js, Java, Docker e Git;
6. resultado dos testes e builds;
7. estado dos containers;
8. caminho Linux, caminho UNC e SHA-256 do APK;
9. branch atual;
10. MCPs conectados, desativados e pendentes;
11. IP Tailscale, MagicDNS e fingerprint SSH do host;
12. resultado do teste de acesso pelo Termux;
13. caminho e resultado do envio do manual ao Telegram;
14. autenticacoes humanas pendentes;
15. confirmacao de que nenhuma chave privada foi transmitida;
16. confirmacao de que o runtime nao depende do Google Cloud.

## Prompt curto para iniciar

Entregar este arquivo ao Codex operando no WSL e enviar:

```text
Leia integralmente e execute de forma autonoma e mandataria o arquivo
docs/CODEX_PROVISIONAMENTO_AUTONOMO_ANTIGRAVITY_WINDOWS.md. Configure todo o
ambiente de desenvolvimento dentro do WSL no caminho
/home/eretazan/all-in-one. Substitua qualquer base existente por um clone limpo
de https://github.com/interflownex/All-in-One.git na branch main, preservando a
base anterior somente como backup em /home/eretazan/backups. Nao use /mnt/c
para o repositorio. Instale e execute Antigravity Linux, Docker Engine e todas
as ferramentas somente dentro do WSL. Nao instale Antigravity, Docker Desktop
ou toolchains no Windows. Configure OpenSSH e Tailscale no WSL para acesso pelo
Termux do celular, mantendo chaves privadas somente no dispositivo de origem.
Envie ao Telegram apenas o manual, chaves publicas, fingerprints e estado,
nunca credenciais ou chaves privadas. Nao dependa do ambiente Google. Continue
ate cumprir todos os criterios e apresente o relatorio final exigido.
```
