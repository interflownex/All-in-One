# Status

- Estado: `journey_react_shell`
- Shell atual: `apps/all-in-one` com pacote `@all-in-one/user-shell`.
- Evidencia: `tests/e2e/test_all_in_one_user_shell.py` cobre a jornada
  consumidor inicial em Playwright desktop/mobile, percorrendo Identity, Wallet,
  Marketplace Orders, Delivery e Jobs com rotas `/gateway/...` interceptadas.
- Dependencia: API Hub e Identity baseline ativos.
- Pendente: ampliar a jornada para API Hub vivo e acoes reais de cadastro,
  wallet, pedido, entrega e candidatura.
