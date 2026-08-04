# AIO MCP Gateway

Gateway MCP remoto e centralizado do ecossistema **All in One + Valley**.

## Estado desta entrega

- MCP Streamable HTTP em `/mcp`;
- saúde independente em `/health`;
- metadata OAuth Protected Resource em `/.well-known/oauth-protected-resource`;
- dez ferramentas somente de leitura;
- OAuth 2.0/OIDC com validação de issuer, audience, assinatura, expiração e JWKS;
- escopos mínimos por ferramenta;
- validação de `Origin` quando presente;
- rate limit local no desenvolvimento e Redis obrigatório em produção;
- `request_id`, `traceparent`, logs JSON e redaction;
- contêiner sem usuário root e com healthcheck;
- CI com Ruff, mypy, pytest, auditoria, Trivy, SBOM e proveniência;
- template Cloud Run por digest e rollback declarativo;
- DNS MCP declarado sob `brasildesconto.com.br`.

Nenhum token, chave, senha ou client secret é versionado. DNS, TLS, provedor OIDC, Redis, imagem publicada e Gemini Spark só podem ser marcados como concluídos após evidência real.

## Endpoints

Produção canônica:

- MCP: `https://mcp.brasildesconto.com.br/mcp`
- Saúde: `https://mcp.brasildesconto.com.br/health`
- Metadata OAuth: `https://mcp.brasildesconto.com.br/.well-known/oauth-protected-resource`

Ambientes reservados:

- `staging-mcp.brasildesconto.com.br`
- `preview-mcp.brasildesconto.com.br`

Aliases opcionais, todos apontando para o mesmo gateway:

- `mcp-valley.brasildesconto.com.br`
- `mcp-rider.brasildesconto.com.br`
- `mcp-admin.brasildesconto.com.br`

Os aliases não criam implementações paralelas. O isolamento ocorre por escopo, tenant e autorização.

## Execução local

```bash
cd services/aio-mcp-gateway
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
uvicorn main:app --host 127.0.0.1 --port 8080
curl --fail http://127.0.0.1:8080/health
```

No desenvolvimento, `AUTH_REQUIRED=false` e o rate limit usa memória. O arquivo `.env.example` documenta as variáveis sem armazenar valores secretos.

## Produção fail-closed

Quando `DEPLOYMENT_ENV=production`, são obrigatórios:

- `OIDC_ISSUER`
- `OIDC_AUDIENCE`
- `OIDC_JWKS_URL`
- `OIDC_ALGORITHMS`
- `REDIS_URL`
- `ALLOWED_ORIGINS`
- `PROTECTED_RESOURCE_URL`

Configuração ausente impede a inicialização. Falha do Redis bloqueia a requisição com HTTP 503.

O token é aceito somente pelo cabeçalho HTTP de autorização. Tokens em query string não são aceitos.

## Escopos

Escopo-base:

- `aio:mcp:read`

Escopos adicionais:

- `aio:github:read`
- `aio:documents:read`
- `aio:valley:read`
- `aio:rider:read`
- `aio:admin:read`

Ferramentas mutáveis continuam proibidas nesta fase.

## Testes e supply chain

```bash
ruff check .
ruff format --check .
mypy main.py security.py deploy/render_cloud_run.py deploy/rollback_cloud_run.py
pytest
python -m compileall -q main.py security.py deploy tests
pip-audit --strict --progress-spinner off
cyclonedx-py environment --output-format JSON --output-file sbom.cdx.json
```

O workflow também constrói o contêiner, verifica `/health`, bloqueia vulnerabilidades High e Critical, gera SBOMs, publica evidências e cria atestação na `main`.

## Ferramentas MCP

- `project_status`
- `list_pending_tasks`
- `search_repository`
- `read_project_document`
- `create_technical_report`
- `valley_consumer_status`
- `valley_rider_status`
- `aio_admin_status`
- `list_recent_pull_requests`
- `inspect_failed_jobs`

Todas usam `readOnlyHint=true` e `destructiveHint=false`.

## DNS Cloudflare

Plano declarativo:

```text
config/cloudflare/mcp_dns_plan.json
```

Validação sem alteração:

```bash
python3 scripts/configure_cloudflare_mcp_dns.py --check --environment production
```

Aplicação explícita:

```bash
python3 scripts/configure_cloudflare_mcp_dns.py --apply --environment production --confirm-zone brasildesconto.com.br --verify-https
```

As credenciais Cloudflare e o target do origin devem ser fornecidos exclusivamente pelo ambiente seguro. O configurador não altera o domínio raiz, não cria wildcard, não aceita URL como CNAME, não remove registros e não sobrescreve conflito de tipo.

## Cloud Run por digest

Template:

```text
deploy/cloud-run-service.template.yaml
```

Renderização e validação são feitas por:

```text
deploy/render_cloud_run.py
```

O script exige imagem no formato `registry/caminho@sha256:digest`, conta de serviço, projeto e região. A aplicação exige `--apply` e confirmação explícita do nome `aio-mcp-gateway`.

Secrets esperados no Secret Manager:

- `aio-mcp-oidc-issuer`
- `aio-mcp-oidc-audience`
- `aio-mcp-oidc-jwks-url`
- `aio-mcp-redis-url`

## Rollback

O rollback é feito por:

```text
deploy/rollback_cloud_run.py
```

O script aceita somente revisões do serviço `aio-mcp-gateway`, valida a revisão antes da mudança e direciona 100% do tráfego para ela. A aplicação exige confirmação explícita.

## Ordem de homologação

1. publicar a imagem e registrar o digest;
2. provisionar conta de serviço e secrets externos;
3. renderizar e aplicar o manifesto;
4. validar a URL nativa do Cloud Run;
5. fornecer o target DNS pelo ambiente seguro;
6. aplicar o DNS Cloudflare;
7. validar TLS e `/health`;
8. validar OAuth e escopos no endpoint MCP;
9. testar no Gemini Spark;
10. somente então declarar produção concluída.
