# Status

- Estado: `api_hub_live_actions`
- Evidencia: `tests/e2e/test_all_in_one_business_shell.py` cobre a jornada
  Business inicial em Playwright desktop/mobile, percorrendo Companies, Catalog
  Offers, Job Postings, Applications e Resume Access Logs com rotas
  `/gateway/...` interceptadas, e tambem cobre API Hub vivo com aprovacao de
  empresa, publicacao de vaga e registro auditavel de acesso a curriculo.
- Dependencia: API Hub e Identity baseline ativos.
- Pendente: ampliar telas Business para acoes reais de ERP/relatorios e
  operacoes de dominio alem de Jobs.
