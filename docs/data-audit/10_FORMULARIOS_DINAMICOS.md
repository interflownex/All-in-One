# Construtor de Formulários Dinâmicos

**Status:** proposta mandatória, ainda não comprovada como implementação.

## Modelo versionado

A proposta contém 14 estruturas: `form_definitions`, `form_versions`, `form_blocks`, `form_fields`, `field_catalog`, `field_bindings`, `form_calculations`, `form_validations`, `form_visibility_rules`, `form_permissions`, `form_homologations`, `form_publications`, `form_submissions`, `form_submission_values`. Cada campo está enumerado em `artifacts/formulario_dinamico_modelo.json`.

## Ciclo de vida

`draft`, `editing`, `submitted`, `under_review`, `changes_requested`, `approved`, `published`, `suspended`, `retired`, `rejected`. Uma versão publicada é imutável; qualquer alteração cria nova versão e passa novamente por homologação.

## Segurança

O modelo exige allowlists de campo, componente e operador; parser seguro; validação e recálculo backend; limite de complexidade; detecção de ciclos; isolamento por tenant; RBAC; ABAC; checksum; auditoria; rollback e sandbox de prévia.

São proibidos seleção arbitrária de tabela/coluna, SQL, JavaScript, shell, desativação de auditoria, enfraquecimento de validação e publicação sem homologação.

## Cobrança

Eventos faturáveis estão separados de autosave e rascunho. Valores e estratégia comercial não são expostos; dependem de aprovação formal.

## Gate de implementação

Migration reversível, backend, frontend, testes de segurança e homologação permanecem `false`. Portanto, este documento é modelagem e não afirma funcionalidade existente.

EVIDÊNCIAS: `config/data_audit/dynamic_form_model_proposal.json`, `artifacts/formulario_dinamico_modelo.json`, `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583`. Lacuna: `AUD-P1-004`.
