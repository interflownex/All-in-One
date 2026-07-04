# Status

- Estado: `live_shell_integrado`
- Dependencia: API Hub, Identity, Finance, Jobs, Delivery e Mobility baseline ativos.
- Concluido: shell do usuario em `all-in-one-user` consumindo `gateway/status`, `gateway/insights/commercial`, `gateway/catalog/offers`, `wallets`, `vacancies` e health dos modulos com fallback de demonstracao e filtro local.
- Validacao: `npm run build` em `apps/all-in-one-user`; `./.venv/bin/python -m pytest -q tests/e2e/test_all_in_one_user_shell.py` com `2 passed`; e regressao conjunta com Business em `./.venv/bin/python -m pytest -q tests/e2e/test_all_in_one_business_shell.py tests/e2e/test_all_in_one_user_shell.py` com `6 passed`.
- Pendente: expandir outras jornadas do app, incluir mobile e aumentar a cobertura Playwright.
