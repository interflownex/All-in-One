# AIO MCP Gateway

Servidor MCP remoto do ecossistema **All in One + Valley**.

## Estado desta entrega

- MCP Streamable HTTP em `/mcp`;
- endpoint de saúde em `/health`;
- execução stateless, adequada a escalabilidade horizontal;
- dez ferramentas iniciais, todas somente de leitura;
- bloqueio básico de consultas sensíveis e path traversal;
- contêiner sem usuário root;
- CI com Ruff, mypy, pytest, compilação e smoke test do contêiner.

OAuth, Secret Manager, domínio e deploy permanecem condicionados às credenciais e à infraestrutura externa. O código não contém segredos nem placeholders de segredo.

## Execução local

```bash
cd services/aio-mcp-gateway
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
uvicorn main:app --host 127.0.0.1 --port 8080
```

Verificação de saúde:

```bash
curl --fail http://127.0.0.1:8080/health
```

Endpoint MCP:

```text
http://127.0.0.1:8080/mcp
```

## Testes

```bash
ruff check .
mypy main.py
pytest
python -m compileall -q main.py tests
```

## Ferramentas

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

## Cloud Run

O contêiner respeita a variável `PORT` fornecida pelo Cloud Run e expõe `/health` para probes. A publicação deve usar conta de serviço dedicada, Secret Manager e privilégio mínimo.

Exemplo de build local:

```bash
docker build -t aio-mcp-gateway .
docker run --rm -p 8080:8080 aio-mcp-gateway
```

## Segurança

- não aceitar tokens por query string;
- não registrar cabeçalhos `Authorization`;
- não disponibilizar ferramentas mutáveis antes da camada de confirmação;
- não permitir leitura de `.env`, chaves privadas ou credenciais;
- não adicionar credenciais ao repositório;
- validar emissor, audiência, validade e escopos quando OAuth for integrado.
