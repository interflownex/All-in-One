# all-in-one-riders

Candidatura, veiculos, entregas, corridas, ganhos e ocorrencias.

Shell React/Vite dedicado para a jornada candidatura -> documento -> veiculo
-> entrega/corrida -> ganhos.

## Contrato operacional

- Pacote: `@all-in-one/riders-shell`.
- Fonte de API: `VITE_API_HUB_URL`.
- Endpoints conectados via API Hub: `/riders/resources/rider_profiles`,
  `/riders/resources/vehicles`, `/delivery/resources/delivery_requests` e
  `/mobility/resources/rides`.
- Fallback local preserva a tela quando o API Hub nao estiver rodando.
- Evidencia versionada: `config/apps/frontend_journeys.json`.
