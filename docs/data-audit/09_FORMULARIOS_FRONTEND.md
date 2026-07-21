# Formulários, Tabelas, Filtros e Dashboards

A varredura localizou 299 superfícies SmartCRUD, sendo 129 formulários, 1067 combinações superfície/campo e 1111 ocorrências de ação. O componente genérico oferece somente `name`, `description` e `category` nos formulários; 985 bindings são genéricos/não comprovados e 82 coincidem provavelmente com campo físico.

O contrato compartilhado de `Salvar Registro` usa `POST {user_id,payload}` na criação e `PATCH {payload}` na edição, com correlação e idempotência na criação. A matriz registra 0 ações incompatíveis. Há 680 ocorrências sem gate explícito de permissão no frontend; autorização backend ou fallback local deve ser analisado por ação.

EVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx`, `modules/shared/runtime.py`, `artifacts/matriz_formulario_campo.csv`, `artifacts/matriz_acao_ui_backend.json`. Lacuna remanescente: `AUD-P1-002`.
