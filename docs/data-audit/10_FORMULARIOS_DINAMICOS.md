# Construtor de Formulários Dinâmicos

**Status:** proposta mandatória, ainda não comprovada como implementação.

## Modelo versionado

A proposta contém 15 estruturas: `form_definitions`, `form_versions`, `form_blocks`, `form_fields`, `field_catalog`, `field_bindings`, `form_calculations`, `form_validations`, `form_visibility_rules`, `form_permissions`, `form_homologations`, `form_publications`, `form_submissions`, `form_submission_values`, `form_billing_events`. Cada campo está enumerado em `artifacts/formulario_dinamico_modelo.json`.

## Ciclo de vida

`draft`, `editing`, `submitted`, `under_review`, `changes_requested`, `approved`, `published`, `suspended`, `retired`, `rejected`. Uma versão publicada é imutável; qualquer alteração cria nova versão e passa novamente por homologação.

## Segurança

O modelo exige allowlists de campo, componente e operador; parser seguro; validação e recálculo backend; limite de complexidade; detecção de ciclos; isolamento por tenant; RBAC; ABAC; checksum; auditoria; rollback e sandbox de prévia.

São proibidos seleção arbitrária de tabela/coluna, SQL, JavaScript, shell, desativação de auditoria, enfraquecimento de validação e publicação sem homologação.

## Cobrança

Eventos faturáveis estão separados de autosave e rascunho. Valores e estratégia comercial não são expostos; dependem de aprovação formal.

## Gate de implementação

Migration reversível, backend transacional, APIs tipadas, builder web responsivo, pré-visualização e testes de segurança HTTP/domínio e QA visual estão implementados. Integração PostgreSQL viva e homologação operacional permanecem pendentes; portanto, o produto ainda não é declarado operacional.

EVIDÊNCIAS: `config/data_audit/dynamic_form_model_proposal.json`, `database/postgres/migrations/028_dynamic_forms_governance.sql`, `modules/dynamic_forms/main.py`, `modules/shared/dynamic_forms.py`, `modules/shared/dynamic_forms_postgres_store.py`, `apps/all-in-one/src/pages/DynamicFormBuilder.tsx`, `tests/test_dynamic_forms_api.py`, `tests/test_dynamic_forms_domain.py`, `tests/test_dynamic_forms_migration.py`, `artifacts/formulario_dinamico_modelo.json`. Lacuna parcial: `AUD-P1-004`.
