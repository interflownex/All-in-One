# APIs, Eventos e Integrações

A varredura AST localizou 112 endpoints, 8 declarações de `response_model` e 150 ocorrências de campo em modelos Pydantic locais. Também foram encontradas 187 transições com 180 nomes de evento. Todos os produtores persistentes passam pelo envelope v1 compartilhado, que registra produtor, payload sanitizado, dados proibidos, idempotência, correlação, causação, timestamp, tenant, usuário, origem, retenção, falha, replay e compatibilidade. A lacuna remanescente é declarar e homologar consumidores downstream reais para cada evento.

EVIDÊNCIAS: `modules/shared/event_contract.py`, `tests/test_event_contract.py`, `artifacts/catalogo_apis.json`, `artifacts/catalogo_eventos.json`, `artifacts/matriz_api_campo.csv`, `artifacts/matriz_evento_campo.csv` e `artifacts/matriz_permissao_acao.csv`. Lacuna parcial: `AUD-P1-003`.
