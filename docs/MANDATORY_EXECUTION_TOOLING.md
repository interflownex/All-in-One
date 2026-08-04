# Ferramentas Mandatórias de Execução

## Escopo

Esta política se aplica às atividades de auditoria, correção, implantação, CI/CD, dependências, Cloudflare e MCP no projeto All in One + Valley.

## GitHub

O plugin GitHub deve permanecer nativo e ativo durante toda a tarefa. Nenhuma conclusão pode ser baseada apenas em memória ou relatório antigo.

Toda rodada deve consultar diretamente:

- repositório e branch padrão;
- issues abertas;
- Pull Requests abertas e duplicadas;
- commits recentes e branches divergentes;
- checks e workflow runs;
- alertas e PRs do Dependabot;
- configuração de merge.

Alterações devem usar branch própria, Pull Request e integração exclusiva por Squash and Merge. É obrigatório validar todos os gates no mesmo head SHA e informar `expected_head_sha` no merge. Push direto na `main`, Merge Commit, Rebase Merge e auto-merge são proibidos.

## Cloudflare

Quando a atividade envolver Pages, Workers, DNS ou domínio, deve existir validação direta pelo conector oficial. Na ausência temporária do conector, a execução deve usar Wrangler ou API oficial com credenciais fornecidas por cofre externo. A tarefa permanece incompleta até comprovar:

- branch de produção;
- deploy mais recente;
- domínio customizado;
- certificado TLS;
- redirects;
- headers de segurança;
- separação entre preview e produção;
- plano de rollback.

Nenhum token Cloudflare pode ser gravado no Git, em logs ou em artefatos.

## MCP Apps

A fonte única do gateway é `services/aio-mcp-gateway`. O protocolo deve permanecer em `/mcp` usando Streamable HTTP, com `/health` independente.

Antes de produção são obrigatórios:

- OAuth 2.0/OIDC com validação de issuer, audience, assinatura, expiração e JWKS;
- escopos por ferramenta;
- rate limit;
- logs estruturados com redaction;
- request_id e trace_id;
- `ruff format --check`;
- `pip-audit`;
- scan Trivy;
- SBOM e proveniência;
- secrets externos;
- imagem referenciada por digest;
- HTTPS, DNS e certificado válidos;
- rollback;
- validação no Gemini Spark.

Ferramentas mutáveis permanecem proibidas até autorização, escopo e confirmação explícita.

## Dependabot e marcações vermelhas

Dependabot é parte permanente de toda varredura. Atualizações major exigem build e testes de compatibilidade. Nenhuma PR pode ser integrada com checks vermelhos, ausentes, cancelados ou ainda em processamento.

## Bloqueios

Falhas de billing, DNS, certificado, credencial ou conector não podem ser mascaradas. O bloqueio deve ser registrado e a tarefa marcada como incompleta até sua resolução legítima.
