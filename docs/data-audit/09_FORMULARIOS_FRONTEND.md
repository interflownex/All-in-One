# Formulários, Tabelas, Filtros e Dashboards

A varredura localizou 272 superfícies SmartCRUD, sendo 128 formulários, 786 combinações superfície/campo e 979 ocorrências de ação. O componente usa contratos versionados gerados das migrations e regras de domínio; 751 bindings apontam para DTO, endpoint e coluna física, e 35 permanecem sem comprovação estática.

O contrato compartilhado de `Salvar Registro` usa `POST {user_id,payload}` na criação e `PATCH {payload}` na edição, com correlação e idempotência na criação. A matriz registra 0 ações incompatíveis. Há 576 ocorrências sem gate explícito de permissão no frontend; autorização backend ou fallback local deve ser analisado por ação.

EVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx`, `modules/shared/runtime.py`, `artifacts/matriz_formulario_campo.csv`, `artifacts/matriz_acao_ui_backend.json`. Lacuna remanescente: `AUD-P1-002`.
