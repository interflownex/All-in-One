# Implantacao

## Desenvolvimento

1. Configure `.env` a partir de `.env.example`, sem credenciais reais no Git.
2. Execute `docker compose -f infra/docker/docker-compose.yml up --build`.
3. Aplique migrations automaticamente pelo container `migrations` ou rode
   `psql` em ambiente limpo.
4. Consulte Identity em `http://localhost:8101/health`, API Hub em
   `http://localhost:8100/health` e Jobs em `http://localhost:8112/health`.

## Producao

Os manifests Kubernetes sao uma base declarativa, nao um deploy autorizado.
Substitua secrets por vault/KMS, configure TLS, bancos gerenciados, backups,
observabilidade, WAF, network policy e imagens imutaveis antes de promover.
