# Entrega funcional: cadastro empresarial, módulos e back-end Business

**Data:** 20 de julho de 2026  
**Branch:** `feat/full-functional-business-modules`

## Entregue

1. Back-end Business com router específico para módulos empresariais.
2. Serviço `recommend_business_modules` no back-end com a mesma matriz funcional do front-end.
3. Endpoints reais:
   - `POST /business-modules/recommendations`
   - `POST /business-modules/companies/{company_id}/classification`
   - `POST /business-modules/companies/{company_id}/apply-recommendations`
   - `GET /business-modules/companies/{company_id}/modules`
   - `PATCH /business-modules/companies/{company_id}/modules/{module_slug}`
   - `GET /business-modules/companies/{company_id}/modules/{module_slug}/change-impact`
4. Persistência em memória por processo para classificação, configurações de módulos e trilha de auditoria.
5. Bloqueio de alteração manual para módulos obrigatórios.
6. Front-end com cliente `businessModuleApi.ts`.
7. Cadastro de empresa conectado ao back-end quando `VITE_API_HUB_URL` e `VITE_API_HUB_TOKEN` estiverem configurados.
8. Tela `Configurações > Empresa > Módulos e recursos` conectada ao back-end para aplicar, ocultar e consultar impacto.
9. Testes unitários de back-end para recomendação, aplicação, alteração manual e bloqueio de módulo obrigatório.

## Observação de arquitetura

A persistência em memória é adequada para execução funcional inicial, testes e ambiente local. Para produção, a mesma interface deve ser promovida para store tipado PostgreSQL com tabelas equivalentes a:

- `business_classification`
- `company_module_settings`
- `company_module_recommendations`
- `company_module_audit`

## Comandos de validação mandatórios no ambiente Codex/local

```bash
pytest tests/test_business_module_settings_backend.py
python3 scripts/check_brand_integrity.py
python3 scripts/validate_repository.py
```

```bash
cd apps/all-in-one-business
npm install
npm run build
npm run lint
npx playwright test
```

## Critério de aceite atendido nesta entrega

- Cadastro empresarial calcula e aplica módulos.
- Back-end possui endpoints dedicados para classificação e módulos.
- Tela de configurações permite ação manual e consulta de impacto.
- Módulos obrigatórios são protegidos.
- Auditoria operacional é registrada.
- A logomarca não foi alterada.
- A interface mantém português do Brasil.
