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
- A interface viva mostra governanca clinica com consentimento LGPD,
  prontuario protegido e retorno pos-consulta sem expor dado sensivel.
- Fallback local preserva a tela quando o API Hub nao estiver rodando.
- Evidencia versionada: `config/apps/frontend_journeys.json`.

## Incremento aprovado: Health Watch + SafeZone

O aplicativo Health sera a superficie principal para configurar e acompanhar a
futura integracao Android/Wear OS:

- vinculo entre usuario, responsavel, celular e smartwatch;
- sinais e exercicios disponibilizados pelo dispositivo;
- registro `Senti Agora`;
- cercas virtuais permanentes, temporarias, por data, horario e recorrencia;
- alertas de saida, bateria baixa e dispositivo offline;
- incidentes, confirmacoes e localizacao temporaria;
- consentimentos, revogacao e protecao contra rastreamento oculto.

A prioridade e `P0_CRITICA` para privacidade, vinculo, contratos, SafeZone,
offline e testes. Android e Wear OS compoem o MVP; Apple permanece fora da
primeira etapa por decisao economica.

Documentacao:

- `docs/HEALTH_WATCH_SAFEZONE.md`;
- `docs/HEALTH_WATCH_SAFEZONE_PRIORITIES.md`.

Os novos diretorios Android/Wear OS so devem ser registrados em `apps/` quando
existir scaffold compilavel e atualizacao coordenada do catalogo e dos
artefatos gerados.

## Revalidacao de integracao

Branch sincronizada logicamente com a `main` estabilizada em 28/07/2026 para
novo ciclo completo de CI, sem desativacao ou flexibilizacao de gates.
