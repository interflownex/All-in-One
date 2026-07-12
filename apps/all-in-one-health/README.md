# all-in-one-health

Pacientes, profissionais, agenda, prontuario e telemedicina.

Shell React/Vite dedicado para a jornada paciente -> agenda -> prontuario ->
consulta.

## Contrato operacional

- Pacote: `@all-in-one/health-shell`.
- Fonte de API: `VITE_API_HUB_URL`.
- Endpoints conectados via API Hub: `/health/resources/patients`,
  `/health/resources/appointments`, `/identity/resources/consents` e
  `/document/resources/documents`.
- Fallback local preserva a tela quando o API Hub nao estiver rodando.
- Evidencia versionada: `config/apps/frontend_journeys.json`.
