# Contrato: Health

## Descricao

Pacientes, prontuario, consulta, telemedicina, prescricao, leitos, convenios,
wearables e protecao SafeZone.

## Entidades atuais

- `patients`
- `appointments`
- `medical_records`
- `prescriptions`
- `beds`

## Entidades aprovadas para incremento

### Wearables

- `wearable_devices`
- `device_capabilities`
- `health_observations`
- `workout_sessions`
- `symptom_markers`
- `telemonitoring_sessions`
- `consent_grants`
- `data_provenance`

### SafeZone

- `care_relationships`
- `safe_zones`
- `safe_zone_schedules`
- `location_samples`
- `location_incidents`
- `incident_escalations`
- `device_status_events`
- `guardian_notifications`
- `temporary_tracking_sessions`

Rotas seguras, `safe_routes`, `route_waypoints` e regras de nao chegada ficam
classificadas como P2.

## APIs atuais

- `GET /health`
- `GET /version`
- `GET /status`
- `GET /metrics`
- `GET /catalog`
- `POST /resources/{resource_type}`
- `GET /resources/{resource_type}`
- `GET /resources/{resource_type}/{resource_id}`
- `PATCH /resources/{resource_type}/{resource_id}`
- `DELETE /resources/{resource_type}/{resource_id}`
- `POST /resources/{resource_type}/{resource_id}/actions/{action}`
- `GET /audit/events`
- `GET /events/outbox`
- `POST /create`
- `GET /{id}`
- `PATCH /{id}`
- `DELETE /{id}`
- `GET /list`
- `POST /approve`
- `POST /reject`
- `POST /audit`

## APIs P0 planejadas

```http
POST   /v1/health/wearables/devices/link
DELETE /v1/health/wearables/devices/{device_id}/unlink
GET    /v1/health/wearables/devices/{device_id}/capabilities
POST   /v1/health/wearables/observations/batch
POST   /v1/health/wearables/symptoms
POST   /v1/health/safezone/zones
GET    /v1/health/safezone/zones
PATCH  /v1/health/safezone/zones/{zone_id}
DELETE /v1/health/safezone/zones/{zone_id}
POST   /v1/health/safezone/locations/batch
POST   /v1/health/safezone/incidents
POST   /v1/health/safezone/incidents/{incident_id}/acknowledge
POST   /v1/health/safezone/incidents/{incident_id}/resolve
```

Esses endpoints permanecem `planned` ate implementacao, migracao e testes.

## Eventos atuais

- `health.appointment.created`
- `health.telemedicine.started`
- `health.prescription.issued`

## Eventos planejados

- `health.wearable.device_linked.v1`
- `health.observation.received.v1`
- `health.workout.completed.v1`
- `health.symptom.marked.v1`
- `health.safezone.created.v1`
- `health.safezone.activated.v1`
- `health.safezone.entered.v1`
- `health.safezone.exited.v1`
- `health.safezone.incident_opened.v1`
- `health.safezone.incident_acknowledged.v1`
- `health.safezone.incident_resolved.v1`
- `health.safezone.device_battery_low.v1`
- `health.safezone.device_offline.v1`

## Regras

- `user_id` e obrigatorio em todo recurso operacional e referencia `identity.users`.
- Exclusao e logica; registros clinicos, de aprovacao e auditoria seguem a politica de retencao aplicavel.
- Aprovacao e rejeicao exigem ator autenticado, justificativa e log imutavel.
- A empresa ou profissional deve estar aprovado antes de uma operacao publica.
- Wearables e SafeZone permanecem capacidades internas do Health.
- Nenhum dominio externo pode ser acessado por leitura direta de tabela.
- Toda observacao deve preservar dispositivo, origem, horario, unidade e procedencia.
- Toda localizacao deve possuir finalidade, regra ativa e autorizacao valida.
- Rastreamento ao vivo deve ser temporario e encerrado automaticamente.

## Seguranca e permissoes

Mutacoes dependem de OAuth2/JWT ou API key no gateway e do escopo do modulo.
O runtime inicial representa o ator por `X-Actor-User-Id` e registra auditoria;
o gateway deve validar a credencial antes do repasse.

Consentimentos de saude, localizacao, telemonitoramento e circulo de cuidado
devem ser independentes, revogaveis e auditaveis.

## Monetizacao

Plano setorial, faturamento medico conveniado e, futuramente, recursos premium
de acompanhamento familiar e clinico. O desenvolvimento do MVP nao pode
depender de API, licenca ou infraestrutura obrigatoriamente paga.

## Integracoes e erros

Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
`401` ator ausente, `403` escopo ou consentimento invalido, `404` recurso
inexistente, `409` vinculo ou idempotencia conflitante e `422` regra de
validacao ou politica antiabuso violada.

## Auditoria

`POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
que e append-only no PostgreSQL. Acesso a localizacao e dados de saude deve
registrar ator, finalidade, recurso, horario e resultado.
