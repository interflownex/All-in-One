# AIO MCP Gateway — Especificação de Produção

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

## Contrato HTTP

- `GET /health`: saúde básica, sem autenticação e sem dados confidenciais.
- `/mcp`: MCP Streamable HTTP, protegido por OAuth 2.0/OIDC quando `DEPLOYMENT_ENV=production` ou `AUTH_REQUIRED=true`.

## Autenticação OIDC

Configuração obrigatória em produção:

- `OIDC_ISSUER`
- `OIDC_AUDIENCE`
- `OIDC_JWKS_URL`
- `OIDC_ALGORITHMS`, padrão `RS256`

O gateway deve validar assinatura, issuer, audience, expiração e algoritmo. Configuração ausente em produção deve impedir a inicialização.

## Escopos

Escopo mínimo padrão para o endpoint MCP:

- `aio:mcp:read`

Escopos adicionais podem ser associados a ferramentas específicas sem liberar mutações.

## Rate limit

- Desenvolvimento: backend em memória permitido.
- Produção: backend Redis obrigatório, usando `REDIS_URL`.
- Limites configuráveis por janela e identidade autenticada.
- Falha do backend em produção deve bloquear a requisição, nunca liberar tráfego sem controle.

## Observabilidade

Cada resposta deve incluir:

- `x-request-id`
- `traceparent`

Logs devem ser estruturados em JSON e remover valores de cabeçalhos e campos relacionados a authorization, token, secret, password e API key.

## Cadeia de suprimentos

CI obrigatório:

- `ruff check .`
- `ruff format --check .`
- `mypy main.py`
- `pytest`
- `pip-audit`
- build do contêiner
- scan Trivy
- SBOM CycloneDX ou SPDX

## Critérios de aceite

- `/health` responde sem autenticação.
- `/mcp` rejeita token ausente ou inválido quando autenticação é obrigatória.
- Configuração incompleta em produção falha na inicialização.
- Rate limit local funciona em desenvolvimento.
- Produção exige Redis.
- Logs não expõem segredos.
- Testes e scans passam no mesmo SHA.
- Endpoint externo, DNS, TLS e Gemini Spark só são declarados concluídos mediante evidência do ambiente real.
