# APIs, Eventos e Integrações

A varredura AST localizou 101 endpoints, 8 declarações de `response_model` e 126 ocorrências de campo em modelos Pydantic locais. Também foram encontradas 194 transições com 187 nomes de evento. Produtor, ação, estados, papéis e MFA vêm das regras do backend; versão, consumidores, payload integral, idempotência e compatibilidade continuam pendentes quando não declarados.

EVIDÊNCIAS: `artifacts/catalogo_apis.json`, `artifacts/catalogo_eventos.json`, `artifacts/matriz_api_campo.csv`, `artifacts/matriz_evento_campo.csv` e `artifacts/matriz_permissao_acao.csv`. Lacuna: `AUD-P1-003`.
