# Status

- Estado: `api_hub_live_actions_filters_audit_self_management`
- Evidencia: `tests/e2e/test_all_in_one_business_shell.py` cobre a jornada
  Business inicial em Playwright desktop/mobile, percorrendo Companies, Catalog
  Offers, Job Postings, Applications e Resume Access Logs com rotas
  `/gateway/...` interceptadas, e tambem cobre API Hub vivo com aprovacao de
  empresa, publicacao de vaga, registro auditavel de acesso a curriculo,
  filtros de status, painel de auditoria operacional e aprovacao viva de API
  clients pelo self-management do API Hub.
- Dependencia: API Hub e Identity baseline ativos.
- Pendente: homologar KYB real, Apigee API Hub e provedores externos quando
  ambiente responsivo e credenciais legitimas estiverem disponiveis.
