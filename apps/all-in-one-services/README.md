# all-in-one-services

Prestadores, visitas, orcamentos, contratos, escrow e avaliacoes.

Shell React/Vite dedicado para a jornada prestador -> visita -> orcamento ->
contrato -> evidencia.

## Contrato operacional

- Pacote: `@all-in-one/services-shell`.
- Fonte de API: `VITE_API_HUB_URL`.
- Endpoints conectados via API Hub: `/services/resources/providers`,
  `/services/resources/service_contracts`, `/finance/resources/escrows` e
  `/document/resources/documents`.
- Fallback local preserva a tela quando o API Hub nao estiver rodando.
- Evidencia versionada: `config/apps/frontend_journeys.json`.
