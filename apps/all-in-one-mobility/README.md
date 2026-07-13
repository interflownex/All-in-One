# all-in-one-mobility

Corridas, transporte publico, tarifas, tickets, QR Code e NFC.

Shell React/Vite dedicado para a jornada corrida -> ticket -> QR/NFC ->
historico.

## Contrato operacional

- Pacote: `@all-in-one/mobility-shell`.
- Fonte de API: `VITE_API_HUB_URL`.
- Endpoints conectados via API Hub: `/mobility/resources/rides`,
  `/mobility/resources/tickets`, `/riders/resources/rider_profiles` e
  `/finance/resources/wallets`.
- A interface viva mostra pos-corrida com rota, operador, ticket QR/NFC,
  wallet e comprovante operacional sem expor token bruto.
- Fallback local preserva a tela quando o API Hub nao estiver rodando.
- Evidencia versionada: `config/apps/frontend_journeys.json`.
