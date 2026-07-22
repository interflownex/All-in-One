# Status

- Estado: `live_shell_integrado`
- Dependencia: Jobs, Delivery e Mobility baseline ativos.
- Concluido: shell mobile conectado a vagas, status de delivery/mobility e alternancia online/offline com fallback visual preservado.
- Validacao: `npm run build` e `./.venv/bin/python -m pytest -q tests/e2e/test_valley_rider.py` com sucesso.
- Pendente: Playwright ampliado para jornadas adicionais e evolucao do shell para mais estados operacionais.
