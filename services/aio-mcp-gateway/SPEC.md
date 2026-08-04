# AIO MCP Gateway - Especificação de Produção

## Objetivo

Disponibilizar um único gateway MCP remoto para o ecossistema All in One + Valley, usando MCP Streamable HTTP em `/mcp` e um endpoint de saúde independente em `/health`.

## Usuários

- Assistentes compatíveis com MCP, incluindo Gemini Spark, após homologação.
- Operadores e desenvolvedores autorizados do ecossistema All in One + Valley.

## Princípios

- Fail-closed em produção.
- Nenhum segredo no repositório, logs ou artefatos.
- Ferramentas somente de leitura nesta fase.
- Escopo mínimo por ferramenta.
- Observabilidade sem conteúdo sensível.
- Deploy reproduzível e reversível.
- Um único gateway produtivo. Aliases DNS não podem criar implementações paralelas.

## Contrato HTTP

- `GET /health`: saúde básica, pública, sem dados confidenciais.
- `/mcp`: MCP Streamable HTTP protegido por OAuth 2.0/OIDC quando `DEPLOYMENT_ENV=production` ou `AUTH_REQUIRED=true`.
- `GET /.well-known/oauth-protected-resource/mcp`: metadados RFC 9728 do recurso protegido.

## DNS MCP

Enquanto não houver outro domínio próprio homologado, todo endpoint MCP que exigir DNS deve usar `brasildesconto.com.br`.

Endpoint canônico de produção:

- `https://mcp.brasildesconto.com.br/mcp`
- `https://mcp.brasildesconto.com.br/health`

Variações reservadas por ambiente:

- `https://mcp-staging.brasildesconto.com.br/mcp`
- `https://mcp-preview.brasildesconto.com.br/mcp`

Aliases funcionais opcionais, todos apontando para o mesmo gateway centralizado:

- `mcp-valley.brasildesconto.com.br`
- `mcp-rider.brasildesconto.com.br`
- `mcp-admin.brasildesconto.com.br`

Os aliases não devem duplicar código, infraestrutura ou bancos. Devem resolver para o mesmo serviço e aplicar isolamento por escopo, tenant e autorização.

DNS, certificado e publicação só podem ser marcados como concluídos após comprovação real no provedor.

## Autenticação OIDC

Configuração obrigatória quando a autenticação estiver ativa:

- `OIDC_ISSUER`
- `OIDC_AUDIENCE`
- `OIDC_JWKS_URL`
- `OIDC_ALGORITHMS`, padrão `RS256`
- `MCP_REQUIRED_SCOPE`, padrão `aio:mcp:read`

O gateway usa o `TokenVerifier` nativo do SDK MCP. Deve validar assinatura, issuer, audience, expiração, subject e algoritmo. Configuração ausente em produção deve impedir a inicialização.

Tokens são aceitos somente no cabeçalho `Authorization: Bearer`. Tokens em query string são proibidos.

## Escopos por ferramenta

| Ferramenta | Escopos mínimos |
|---|---|
| `project_status` | `aio:mcp:read` |
| `list_pending_tasks` | `aio:mcp:read` |
| `search_repository` | `aio:mcp:read`, `aio:github:read` |
| `read_project_document` | `aio:mcp:read`, `aio:documents:read` |
| `create_technical_report` | `aio:mcp:read` |
| `valley_consumer_status` | `aio:mcp:read`, `aio:valley:read` |
| `valley_rider_status` | `aio:mcp:read`, `aio:rider:read` |
| `aio_admin_status` | `aio:mcp:read`, `aio:admin:read` |
| `list_recent_pull_requests` | `aio:mcp:read`, `aio:github:read` |
| `inspect_failed_jobs` | `aio:mcp:read`, `aio:github:read` |

Nenhum escopo desta fase autoriza escrita em Git, banco, arquivos ou infraestrutura.

## Proteção do transporte

- Proteção contra DNS rebinding habilitada.
- Hosts autorizados definidos por `MCP_ALLOWED_HOSTS`.
- Origens autorizadas definidas por `MCP_ALLOWED_ORIGINS`.
- Corpo máximo definido por `MAX_REQUEST_BODY_BYTES`.
- Produção aceita somente o host canônico ou hosts explicitamente homologados.

## Rate limit

- Desenvolvimento: backend em memória permitido.
- Produção: backend Redis obrigatório, usando `REDIS_URL`.
- Limites configuráveis por janela e identidade.
- Falha do backend em produção deve responder 503, nunca liberar tráfego sem controle.

## Observabilidade

Cada resposta deve incluir:

- `x-request-id`
- `traceparent`
- `x-content-type-options: nosniff`
- `cache-control: no-store`
- `referrer-policy: no-referrer`

Logs devem ser estruturados em JSON e remover valores relacionados a authorization, token, secret, password, API key e credenciais.

## Cadeia de suprimentos

CI obrigatório:

- `ruff check .`
- `ruff format --check .`
- `mypy main.py security.py deploy/*.py`
- `pytest`
- `pip-audit --strict`
- compilação Python
- build do contêiner
- smoke test de `/health`
- scan Trivy para vulnerabilidades e segredos
- SBOM CycloneDX da aplicação e da imagem
- atestação na `main`

## Deploy

- Imagem obrigatoriamente referenciada por digest `sha256`.
- Conta de serviço dedicada e privilégio mínimo.
- OIDC e Redis fornecidos por Secret Manager.
- Aplicação exige `--confirm-service aio-mcp-gateway`.
- O manifesto não deve ser aplicado enquanto billing, IAM, secrets e autorização de produção não estiverem comprovados.

## Rollback

- O rollback aceita somente revisões com prefixo `aio-mcp-gateway-`.
- A revisão deve ser validada no Cloud Run antes da troca de tráfego.
- A aplicação exige confirmação explícita do serviço.
- O rollback direciona 100% do tráfego para uma revisão previamente validada.

## Critérios de aceite

- `/health` responde sem autenticação.
- `/mcp` rejeita token ausente, inválido ou sem escopo.
- Metadados OAuth são expostos no caminho RFC 9728 correto.
- Configuração incompleta em produção falha na inicialização.
- Rate limit local funciona em desenvolvimento.
- Produção exige Redis.
- Logs não expõem segredos.
- Testes e scans passam no mesmo SHA.
- Deploy usa imagem por digest e rollback validado.
- Endpoint externo, DNS, TLS e Gemini Spark só são declarados concluídos mediante evidência do ambiente real.
