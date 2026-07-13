# Status

- Estado: `journey_react_shell`
- Shell atual: `apps/all-in-one` com pacote `@all-in-one/user-shell`.
- Evidencia: `tests/e2e/test_all_in_one_user_shell.py` cobre a jornada
  consumidor inicial em Playwright desktop/mobile, percorrendo Identity, Wallet,
  Marketplace Orders, Delivery e Jobs com rotas `/gateway/...` interceptadas; a
  mesma suite tambem sobe API Hub e modulos FastAPI reais para validar Identity,
  Wallet, Marketplace Orders, Delivery e Jobs sem interceptacao, concluindo
  pagamento sandbox de pedido, entrega viva no frontend e candidatura Jobs com
  busca viva, notificacoes e painel pos-candidatura.
- Dependencia: API Hub e Identity baseline ativos.
- Pendente: ampliar notificacoes persistidas e comunicacao com empresa apos
  candidatura Jobs quando houver backend especifico para mensagens.
