# Provisionamento Autonomo do All-in-One no Antigravity IDE

## Instrucao mandataria para o Codex

Este documento e uma ordem de execucao completa para o Codex operando na
maquina Windows do usuario. Ao receber a ordem para executar este arquivo, o
Codex deve realizar todas as etapas abaixo de forma autonoma, sequencial e
verificavel.

O Codex nao deve apenas explicar os comandos. Deve executa-los, corrigir falhas
recuperaveis e continuar ate que todos os criterios de sucesso sejam atendidos.
So e permitido interromper quando uma autenticacao interativa exigir acao
humana ou quando um recurso externo estiver comprovadamente indisponivel.

## Objetivo

Substituir integralmente a base local existente:

```text
C:\Users\ereta\.codex\worktrees\all-in-one
```

pela versao remota oficial:

```text
Repositorio: https://github.com/interflownex/All-in-One.git
Branch: main
Referencia autoritativa: origin/main
```

Depois da substituicao, instalar e configurar o ambiente de desenvolvimento
Windows para uso no Antigravity IDE, incluindo Git, GitHub CLI, PowerShell 7,
Python 3.12, Node.js 22.14.0, Java 17, Docker Desktop, Google Cloud CLI,
dependencias Python, dependencias web, variaveis locais, Docker Compose e
validacoes do repositorio.

## Regras inegociaveis

1. A nuvem, representada por `origin/main`, e a fonte de verdade.
2. O conteudo antigo do diretorio alvo nao pode ser mesclado ou reaplicado
   automaticamente sobre o clone novo.
3. Antes da substituicao, criar um backup fechado e datado fora do diretorio
   alvo.
4. Nunca copiar `.env`, tokens, chaves, credenciais ou configuracoes secretas
   do backup para o clone novo.
5. Nunca executar `git reset --hard` dentro da base antiga.
6. A substituicao deve ser feita movendo a base antiga inteira e clonando uma
   copia limpa no caminho original.
7. Nao apagar o backup automaticamente.
8. Nao versionar `.env`, credenciais ou arquivos gerados.
9. Executar comandos elevados somente quando a instalacao do Windows ou Docker
   exigir.
10. Nao declarar sucesso sem executar os checkpoints deste documento.
11. Preservar os arquivos `AGENTS.md`, `GEMINI.md` e as politicas versionadas
    recebidas de `origin/main`.
12. Depois do clone, todo desenvolvimento deve ocorrer em branch
    `codex/<descricao>`, nunca diretamente em `main`.

## Estado final esperado

Ao concluir:

- o caminho alvo deve ser um clone limpo de `origin/main`;
- `git status --short --branch` nao deve mostrar alteracoes;
- Python deve usar `.venv\Scripts\python.exe`;
- Node.js deve estar na versao definida por `.nvmrc`;
- Docker Desktop deve estar operacional com containers Linux;
- o Docker Compose deve ser valido;
- as dependencias devem estar instaladas;
- as validacoes basicas devem passar;
- o Antigravity IDE deve conseguir abrir o workspace;
- nenhum segredo deve estar versionado.

## Fase 1 - Preflight e inventario

Executar no PowerShell 7:

```powershell
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Target = "C:\Users\ereta\.codex\worktrees\all-in-one"
$Parent = Split-Path $Target -Parent
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupRoot = "C:\Users\ereta\.codex\backups"
$Backup = Join-Path $BackupRoot "all-in-one-before-cloud-$Timestamp"
$Repository = "https://github.com/interflownex/All-in-One.git"
$Branch = "main"

New-Item -ItemType Directory -Force -Path $Parent | Out-Null
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
```

Registrar o inventario da base antiga quando ela existir:

```powershell
if (Test-Path $Target) {
    $Inventory = Join-Path $BackupRoot "all-in-one-inventory-$Timestamp.txt"
    @(
        "Data UTC: $([DateTime]::UtcNow.ToString('o'))"
        "Origem local: $Target"
        "Destino do backup: $Backup"
    ) | Set-Content -Encoding UTF8 $Inventory

    if (Test-Path (Join-Path $Target ".git")) {
        git -C $Target status --short --branch |
            Add-Content -Encoding UTF8 $Inventory
        git -C $Target log -1 --format="%H %cI %s" |
            Add-Content -Encoding UTF8 $Inventory
        git -C $Target remote -v |
            Add-Content -Encoding UTF8 $Inventory
    }
}
```

Se houver processos usando o diretorio, fechar terminais, agentes e janelas do
Antigravity associados ao workspace. O Codex pode encerrar apenas processos
claramente vinculados ao caminho alvo. Nao encerrar processos nao relacionados.

## Fase 2 - Backup e substituicao integral

Sair do diretorio que sera substituido:

```powershell
Set-Location $Parent
```

Mover a base antiga inteira:

```powershell
if (Test-Path $Target) {
    Move-Item -LiteralPath $Target -Destination $Backup
}
```

Clonar exclusivamente a referencia remota:

```powershell
try {
    git clone `
        --branch $Branch `
        --single-branch `
        --origin origin `
        $Repository `
        $Target

    if ($LASTEXITCODE -ne 0) {
        throw "git clone retornou codigo $LASTEXITCODE."
    }

    Set-Location $Target
    git fetch --prune origin
    git checkout $Branch
    git pull --ff-only origin $Branch
} catch {
    Set-Location $Parent

    if (Test-Path $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }

    if (Test-Path $Backup) {
        Move-Item -LiteralPath $Backup -Destination $Target
    }

    throw "Clone remoto falhou e a base anterior foi restaurada: $($_.Exception.Message)"
}
```

Validar que o clone corresponde exatamente a `origin/main`:

```powershell
$LocalHead = git rev-parse HEAD
$RemoteHead = git rev-parse "origin/$Branch"

if ($LocalHead -ne $RemoteHead) {
    throw "Clone local nao corresponde a origin/$Branch."
}

if (git status --porcelain) {
    throw "O clone novo nao esta limpo."
}
```

Depois de um clone valido, o backup deve permanecer intacto em
`C:\Users\ereta\.codex\backups`.

## Fase 3 - Instalar ferramentas obrigatorias

Verificar a existencia do `winget`. Quando disponivel, instalar ou atualizar:

```powershell
$Packages = @(
    "Git.Git",
    "Microsoft.PowerShell",
    "Docker.DockerDesktop",
    "Python.Python.3.12",
    "GitHub.cli",
    "Google.CloudSDK",
    "EclipseAdoptium.Temurin.17.JDK",
    "Schniz.fnm"
)

foreach ($Package in $Packages) {
    winget install `
        --id $Package `
        --exact `
        --silent `
        --accept-package-agreements `
        --accept-source-agreements
}
```

O Codex deve tolerar o retorno que indica pacote ja instalado e verificar o
resultado com o executavel correspondente.

Instalar a versao Node.js exigida pelo repositorio:

```powershell
fnm env --use-on-cd | Out-String | Invoke-Expression
$NodeVersion = (Get-Content ".nvmrc" -Raw).Trim().TrimStart("v")
fnm install $NodeVersion
fnm use $NodeVersion
fnm default $NodeVersion
```

Verificacoes obrigatorias:

```powershell
git --version
pwsh --version
python --version
node --version
npm --version
java -version
docker version
docker compose version
gh --version
gcloud --version
```

Se uma alteracao de `PATH`, instalacao do WSL ou Docker exigir reinicializacao,
o Codex deve concluir as instalacoes, registrar o ponto de retomada e continuar
automaticamente depois da reinicializacao quando o ambiente permitir.

## Fase 4 - Instalar o Antigravity IDE

Verificar se o produto **Antigravity IDE** esta instalado. Ele e diferente do
aplicativo independente **Antigravity 2.0**.

Fonte oficial:

```text
https://antigravity.google/download
```

O Codex deve:

1. procurar primeiro um pacote oficial no `winget`;
2. se nao houver, baixar o instalador Windows x64 da pagina oficial;
3. validar que o dominio de origem e `antigravity.google`;
4. executar o instalador;
5. nunca baixar instaladores de espelhos ou sites de terceiros;
6. abrir o Antigravity IDE ao final;
7. aguardar somente a autenticacao Google interativa, quando solicitada.

## Fase 5 - Ambiente Python

No clone novo:

```powershell
Set-Location $Target

if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force
}

python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
```

Instalar tambem os requisitos dos modulos e workers:

```powershell
Get-ChildItem -Path "modules", "workers" -Filter "requirements.txt" -Recurse |
    ForEach-Object {
        & ".\.venv\Scripts\python.exe" -m pip install -r $_.FullName
    }
```

Instalar o navegador de testes:

```powershell
& ".\.venv\Scripts\python.exe" -m playwright install chromium
```

## Fase 6 - Configuracao local segura

Criar `.env` somente quando ele nao existir:

```powershell
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}
```

Gerar uma chave nova para desenvolvimento local:

```powershell
$EncryptionKey = & ".\.venv\Scripts\python.exe" -c `
    "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

$EnvContent = Get-Content ".env" -Raw
$EnvContent = $EnvContent -replace `
    "(?m)^ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY=.*$", `
    "ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY=$EncryptionKey"
$EnvContent | Set-Content -Encoding UTF8 ".env"
```

Garantir valores locais de desenvolvimento, sem credenciais produtivas:

```dotenv
POSTGRES_DB=all_in_one
POSTGRES_USER=all_in_one
POSTGRES_PASSWORD=local-development-only
MONGO_INITDB_DATABASE=all_in_one
RABBITMQ_DEFAULT_USER=all_in_one
RABBITMQ_DEFAULT_PASS=local-development-only
GOOGLE_INTEGRATIONS_ENABLED=true
GOOGLE_CLOUD_ENABLED=true
GOOGLE_AI_STUDIO_ENABLED=true
GOOGLE_CODE_CLI_ENABLED=true
GEMINI_CODE_ASSIST_ENABLED=true
STITCH_REMOTE_SYNC_ENABLED=true
```

`STITCH_API_KEY`, chaves Google e demais segredos devem permanecer vazios ate
serem fornecidos por autenticacao legitima ou secret manager.

Confirmar que `.env` esta ignorado:

```powershell
git check-ignore ".env"
```

## Fase 7 - Configurar Antigravity e extensoes

Abrir o diretorio:

```text
C:\Users\ereta\.codex\worktrees\all-in-one
```

No workspace, o Antigravity deve respeitar:

```text
AGENTS.md
GEMINI.md
.agents\antigravity.json
config\autonomy\multi_agent_sync_policy.json
```

Instalar as extensoes disponiveis equivalentes a:

```text
ms-python.python
ms-python.vscode-pylance
ms-python.debugpy
charliermarsh.ruff
ms-azuretools.vscode-docker
ms-vscode.powershell
redhat.vscode-yaml
esbenp.prettier-vscode
dbaeumer.vscode-eslint
github.vscode-github-actions
github.vscode-pull-request-github
eamodio.gitlens
ms-vscode-remote.remote-wsl
ms-kubernetes-tools.vscode-kubernetes-tools
```

Selecionar como interpretador:

```text
C:\Users\ereta\.codex\worktrees\all-in-one\.venv\Scripts\python.exe
```

Se `.vscode\settings.json` apontar para `.venv/bin/python`, criar uma
configuracao local do editor ou selecionar o interpretador pela interface. Nao
fazer commit de uma alteracao especifica de maquina sem necessidade.

## Fase 8 - GitHub e Google Cloud

Verificar a autenticacao:

```powershell
gh auth status
gcloud auth list
```

Se necessario, iniciar os fluxos oficiais:

```powershell
gh auth login --web
gcloud auth login
gcloud auth application-default login
gcloud config set project all-in-one-498012
```

Esses passos podem abrir o navegador. O Codex deve aguardar a conclusao do
login e continuar automaticamente.

Nunca imprimir tokens ou credenciais nos logs.

## Fase 9 - Dependencias web

Instalar dependencias somente nos aplicativos que possuam `package.json`:

```powershell
$Applications = @(
    "apps\all-in-one",
    "apps\all-in-one-business",
    "apps\valley",
    "apps\valley_business",
    "apps\valley_rider",
    "desktop\valley-erp"
)

foreach ($Application in $Applications) {
    if (Test-Path (Join-Path $Application "package.json")) {
        Push-Location $Application
        try {
            if (Test-Path "package-lock.json") {
                npm ci
            } else {
                npm install
            }
        } finally {
            Pop-Location
        }
    }
}
```

## Fase 10 - Docker Desktop e servicos

Iniciar o Docker Desktop quando o daemon nao estiver acessivel. Aguardar ate:

```powershell
docker info
```

Validar o manifesto:

```powershell
docker compose -f infra/docker/docker-compose.yml config --quiet
```

Subir o ambiente:

```powershell
docker compose -f infra/docker/docker-compose.yml up --build -d
```

Verificar:

```powershell
docker compose -f infra/docker/docker-compose.yml ps
docker compose -f infra/docker/docker-compose.yml logs --tail 200
```

O Codex deve investigar containers `unhealthy`, `exited` ou reiniciando,
corrigir configuracoes locais recuperaveis e repetir a validacao.

## Fase 11 - Validacoes obrigatorias

Executar:

```powershell
& ".\.venv\Scripts\python.exe" scripts\scaffold_modules.py --check
& ".\.venv\Scripts\python.exe" scripts\validate_repository.py
& ".\.venv\Scripts\python.exe" -m pytest --import-mode=importlib
```

Testar endpoints essenciais:

```powershell
$HealthEndpoints = @(
    "http://localhost:8100/health",
    "http://localhost:8101/health",
    "http://localhost:8102/health",
    "http://localhost:8112/health",
    "http://localhost:8113/health"
)

foreach ($Endpoint in $HealthEndpoints) {
    $Response = Invoke-WebRequest -UseBasicParsing -Uri $Endpoint -TimeoutSec 15
    if ($Response.StatusCode -ne 200) {
        throw "Healthcheck falhou: $Endpoint"
    }
}
```

Validar builds web:

```powershell
foreach ($Application in $Applications) {
    if (Test-Path (Join-Path $Application "package.json")) {
        Push-Location $Application
        try {
            npm run build
        } finally {
            Pop-Location
        }
    }
}
```

## Fase 12 - Android

Validar que o builder Android pode ser criado:

```powershell
docker build `
    -t all-in-one-android-builder `
    -f infra/docker/android-builder.Dockerfile `
    .
```

Gerar o APK:

```powershell
docker run --rm `
    -v "${Target}:/workspace" `
    -w /workspace/apps/valley-android `
    all-in-one-android-builder `
    bash ./gradlew --no-daemon assembleDebug
```

Confirmar:

```powershell
$Apk = Join-Path $Target `
    "apps\valley-android\app\build\outputs\apk\debug\app-debug.apk"

if (-not (Test-Path $Apk)) {
    throw "APK nao foi gerado."
}

Get-FileHash $Apk -Algorithm SHA256
Get-Item $Apk | Select-Object FullName, Length, LastWriteTime
```

O APK e artefato local e nao deve ser commitado.

## Fase 13 - Higiene e branch de trabalho

Remover somente caches e artefatos reconhecidamente gerados pelo
provisionamento quando necessario. Nao remover o APK solicitado.

Confirmar que o clone base continua sem alteracoes versionaveis:

```powershell
git status --short --branch
git diff --check
```

Criar uma branch para trabalhos futuros:

```powershell
$WorkBranch = "codex/ambiente-local-antigravity"

if (-not (git branch --list $WorkBranch)) {
    git switch -c $WorkBranch
} else {
    git switch $WorkBranch
}
```

Nao criar commit apenas por instalar dependencias, criar `.env` ou gerar
artefatos ignorados.

## Criterios de sucesso

Todos os itens devem ser verdadeiros:

- [ ] a base antiga foi movida para um backup datado;
- [ ] o caminho alvo foi recriado por `git clone`;
- [ ] `HEAD` era igual a `origin/main` imediatamente apos o clone;
- [ ] o repositorio nao recebeu arquivos da base antiga;
- [ ] Python 3.12 e `.venv` estao funcionais;
- [ ] Node.js corresponde a `.nvmrc`;
- [ ] Java 17 esta disponivel;
- [ ] Docker e Docker Compose respondem;
- [ ] o manifesto Compose e valido;
- [ ] as dependencias Python e web foram instaladas;
- [ ] os validadores e testes foram executados;
- [ ] os healthchecks essenciais retornam HTTP 200;
- [ ] o APK debug foi gerado;
- [ ] `.env` esta ignorado pelo Git;
- [ ] o Antigravity IDE abriu o workspace correto;
- [ ] GitHub e Google Cloud foram configurados ou o unico bloqueio restante e
      uma autenticacao humana claramente informada;
- [ ] nenhuma credencial foi exposta;
- [ ] o backup antigo permanece preservado.

## Relatorio final obrigatorio

Ao terminar, o Codex deve responder em portugues do Brasil com:

1. caminho do clone novo;
2. caminho do backup;
3. commit remoto usado como base;
4. versoes de Python, Node.js, Java, Docker e Git;
5. resultado dos testes e validadores;
6. estado dos containers;
7. caminho e SHA-256 do APK;
8. branch atual;
9. eventuais autenticacoes externas ainda pendentes.

Falhas devem incluir o comando, a causa raiz identificada e as tentativas de
recuperacao realizadas. Nao encerrar com uma lista generica de proximos passos
quando a acao puder ser executada autonomamente.

## Prompt curto para iniciar a execucao

Entregar ao Codex local:

```text
Leia integralmente docs/CODEX_PROVISIONAMENTO_AUTONOMO_ANTIGRAVITY_WINDOWS.md
e execute todas as fases. Esta e uma ordem autonoma e mandataria. Substitua
C:\Users\ereta\.codex\worktrees\all-in-one por um clone limpo de
https://github.com/interflownex/All-in-One.git na branch main, preservando a
base anterior somente como backup externo. Nao mescle arquivos antigos no
clone novo. Continue ate cumprir todos os criterios de sucesso e apresente o
relatorio final exigido.
```
