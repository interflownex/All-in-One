# Implantacao

## Desenvolvimento

1. Configure `.env` a partir de `.env.example`, sem credenciais reais no Git.
   Para manter documentos legiveis entre reinicios locais, gere
   `ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY` em base64 URL-safe com 32 bytes.
   O Compose executa Jobs nas tabelas PostgreSQL tipadas por padrao apos
   aplicar as migrations; fora dele, configure `ALL_IN_ONE_JOBS_POSTGRES_DSN`.
   Para publicar a outbox configure `ALL_IN_ONE_OUTBOX_POSTGRES_DSN` e
   `ALL_IN_ONE_RABBITMQ_URL`; o Compose ja fornece valores locais.
   Para coordenar designs Stitch mantenha o MCP obrigatorio em
   `~/.codex/config.toml` apontando para `https://stitch.googleapis.com/mcp`.
   A documentacao oficial usa `http_headers`; neste workspace, persista o
   header por `env_http_headers` e configure a credencial rotacionada em
   `STITCH_API_KEY` apenas no ambiente local/CI.
Para o agente de IA Superdesign, configure `OPENROUTER_API_KEY` no seu ambiente local
e aponte a URL base para `https://openrouter.ai/api/v1`.
   O estado padrao do workspace e `local-first`, sem custo obrigatorio e sem
   dependencia operacional de Google Cloud, AlloyDB ou Stitch remoto.
   Preserve os nomes de variaveis e manifests atuais para que a migracao futura
   para a plataforma Google exija somente reativacao de flags, segredos e DSNs.
   Quando houver verba e contexto para retomar a plataforma Google, reative as
   flags no ambiente e autentique legitimamente o SDK antes de diagnosticar ou
   reativar recursos:

   ```bash
   python3 scripts/google_cloud_control.py status
   python3 scripts/google_cloud_control.py activate --project SEU_PROJETO
   ```

   `activate` habilita as APIs declaradas em
   `config/cloud/google_cloud_profile.json`, inicia somente instancias Compute
   Engine em `TERMINATED` e restaura Cloud SQL com `activationPolicy=NEVER`.
   O comando nao altera billing, nao exclui recursos e nao contorna IAM,
   compliance ou suspensao administrativa.
2. Execute `docker compose -f infra/docker/docker-compose.yml up --build`.
3. Aplique migrations automaticamente pelo container `migrations` ou rode
   `psql` em ambiente limpo.
4. Consulte Identity em `http://localhost:8101/health`, API Hub em
   `http://localhost:8100/health` e Jobs em `http://localhost:8112/health`.
5. Para o contrato de telas, rode `python scripts/stitch_orchestrator.py plan`
   e `python scripts/validate_stitch_mcp_config.py`; com credencial segura
   disponivel, `sync` cria um projeto Stitch por modulo.

## Producao

Os manifests Kubernetes sao uma base declarativa, nao um deploy autorizado.
Substitua secrets por vault/KMS, incluindo
`ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY`; o servico Jobs falha ao iniciar em
producao sem esta chave. Armazene credenciais Stitch apenas em vault/secret e
rotacione qualquer chave exposta em texto. Configure TLS, bancos gerenciados, backups,
observabilidade, WAF, network policy e imagens imutaveis antes de promover.
