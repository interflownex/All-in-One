# Implantacao

## Desenvolvimento

1. Configure `.env` a partir de `.env.example`, sem credenciais reais no Git.
   Para manter documentos legiveis entre reinicios locais, gere
   `ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY` em base64 URL-safe com 32 bytes.
   O Compose executa Jobs nas tabelas PostgreSQL tipadas por padrao apos
   aplicar as migrations; fora dele, configure `ALL_IN_ONE_JOBS_POSTGRES_DSN`.
   Para publicar a outbox configure `ALL_IN_ONE_OUTBOX_POSTGRES_DSN` e
   `ALL_IN_ONE_RABBITMQ_URL`; o Compose ja fornece valores locais.
   Para coordenar designs Stitch configure uma credencial rotacionada em
   `STITCH_API_KEY` ou `STITCH_ACCESS_TOKEN` apenas no ambiente local/CI.
2. Execute `docker compose -f infra/docker/docker-compose.yml up --build`.
3. Aplique migrations automaticamente pelo container `migrations` ou rode
   `psql` em ambiente limpo.
4. Consulte Identity em `http://localhost:8101/health`, API Hub em
   `http://localhost:8100/health` e Jobs em `http://localhost:8112/health`.
5. Para o contrato de telas, rode `python scripts/stitch_orchestrator.py plan`;
   com credencial segura disponível, `sync` cria um projeto Stitch por modulo.

## Producao

Os manifests Kubernetes sao uma base declarativa, nao um deploy autorizado.
Substitua secrets por vault/KMS, incluindo
`ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY`; o servico Jobs falha ao iniciar em
producao sem esta chave. Armazene credenciais Stitch apenas em vault/secret e
rotacione qualquer chave exposta em texto. Configure TLS, bancos gerenciados, backups,
observabilidade, WAF, network policy e imagens imutaveis antes de promover.
