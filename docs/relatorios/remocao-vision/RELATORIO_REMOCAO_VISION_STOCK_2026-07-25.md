# Relatório de remoção do Vision e atualização do STOCK

**Data:** 25/07/2026
**Branch:** codex/remover-vision-atualizar-stock-2026-07-25
**Novo total:** 24 módulos
**Telas previstas:** 171
**Rotas estimadas:** 325
**Varredura:** referências residuais exigem revisão

## Alterações executadas

1. remoção do Vision do catálogo oficial;
2. remoção das páginas, backend, contrato, store, teste e manifesto Kubernetes específicos;
3. retirada das rotas do Vision nos aplicativos web;
4. atualização da Home para 24 módulos e 171 telas;
5. reposicionamento do STOCK na primeira etapa;
6. criação de migração PostgreSQL para remoção do schema Vision;
7. atualização da documentação vigente e preservação das auditorias históricas como evidência.

## Referências residuais fora do histórico

- `STATUS.md`
- `memorandum.md`
- `tests/test_retention_jobs.py`
- `tests/test_postgres_migrations_smoke.py`
- `tests/test_data_subject_rights.py`
- `tests/test_compliance_matrix.py`
- `tests/test_retention_worker.py`
- `tests/test_postgres_priority_stores_integration.py`
- `tests/test_vision_domain.py`
- `scripts/gcp_storage_hygiene.py`
- `scripts/refactor_api_hub.py`
- `scripts/validate_postgres_real_dsn.py`
- `scripts/check_artifact_registry.py`
- `scripts/generate_kubernetes_manifests.py`
- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/EXECUTION_PLAN.md`
- `docs/memorando_status_mercado_abnt.md`
- `docs/DECISAO_24_MODULOS_STOCK_PRIMEIRA_ETAPA_2026-07-25.md`
- `docs/Pendências Do desenvolvedor.md`
- `docs/DIRETRIZ_MANDATORIA_USABILIDADE_COMERCIAL_VALLEY.md`
- `docs/analise_eventos_de_negocio.md`
- `docs/ARCHITECTURE.md`
- `docs/ORIENTACAO_CODEX_SYNC_MARKETPLACE_VALLEY.md`
- `docs/DATABASE.md`
- `docs/catalogo_fisico_dados.md`
- `docs/COMPLIANCE.md`
- `docs/analise_dominios.md`
- `.github/workflows/database.yml`
- `.github/workflows/regenerate-artifacts-24-modules.yml`
- `modules/identity/main.py`
- `modules/api_hub/main.py`
- `modules/shared/valley_catalog.py`
- `apps/valley/src/lib/valleyPlatform.ts`
- `apps/all-in-one-business/src/components/SmartCRUD.tsx`
- `apps/valley-android/app/src/main/assets/valley/assets/index-GcTkAXla.js`
- `apps/all-in-one/src/lib/demoData.ts`
- `apps/all-in-one/src/components/Navigation.tsx`
- `apps/all-in-one/src/components/ModuleDashboard.tsx`
- `apps/all-in-one/src/components/SmartCRUD.tsx`
- `tests/e2e/test_all_in_one_business_shell.py`
- `tests/e2e/conftest.py`
- `config/compliance/retention_jobs.json`
- `config/compliance/data_classification.json`
- `config/compliance/data_subject_rights.json`
- `config/stitch/template_project_coordinate.json`
- `config/stitch/template_project_state.json`
- `infra/ci-cd/cloudbuild-all.yaml`
- `infra/kubernetes/core/db-migrations-cm.yaml`
