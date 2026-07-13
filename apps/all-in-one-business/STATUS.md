# Status

- Estado: `api_hub_live_actions_filters_audit`
- Evidencia: `tests/e2e/test_all_in_one_business_shell.py` cobre a jornada
  Business inicial em Playwright desktop/mobile, percorrendo Companies, Catalog
  Offers, Job Postings, Applications e Resume Access Logs com rotas
  `/gateway/...` interceptadas, e tambem cobre API Hub vivo com aprovacao de
  empresa, publicacao de vaga, registro auditavel de acesso a curriculo,
  filtros de status e painel de auditoria operacional.
- Dependencia: API Hub e Identity baseline ativos.
- Pendente: retomar API Hub admin/self-management dedicado e aprofundar KYB real
  com convites operacionais.
