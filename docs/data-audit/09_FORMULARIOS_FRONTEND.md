# Formulários, Tabelas, Filtros e Dashboards

A varredura localizou 299 superfícies SmartCRUD, sendo 129 formulários, 1067 combinações superfície/campo e 1111 ocorrências de ação. O componente genérico oferece somente `name`, `description` e `category` nos formulários; 985 bindings são genéricos/não comprovados e apenas 82 coincidem provavelmente com campo físico.

A matriz de ações encontrou 129 botões `Salvar Registro` incompatíveis: criação envia payload plano sem o envelope `ResourceCreate`, e edição usa `PUT` embora o backend ofereça `PATCH`. Há 979 ocorrências de ação sem gate explícito de permissão no frontend; autorização backend ou fallback local deve ser analisado por ação.

EVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx`, `modules/shared/runtime.py`, `artifacts/matriz_formulario_campo.csv`, `artifacts/matriz_acao_ui_backend.json`. Lacunas: `AUD-P1-002` e `AUD-P1-008`.
