# All in One Health Watch + SafeZone

**Status:** aprovado para implementação incremental  
**Classificação:** Técnico e Conceitual  
**Público do produto:** B2C, responsáveis familiares, cuidadores, clínicas e profissionais de saúde  
**Plataformas do MVP:** Android e Wear OS  
**Apple:** fora da primeira etapa por decisão econômica  
**Princípio financeiro:** desenvolvimento inicial sem APIs, licenças ou infraestrutura obrigatoriamente pagas

## Objetivo

O Health Watch é a extensão vestível do módulo `health`. Ele reúne monitoramento de sinais disponibilizados pelo dispositivo, exercícios, telemonitoramento autorizado e proteção de dependentes por cercas virtuais.

O recurso não cria um novo módulo. Wearables e SafeZone são capacidades internas do Health e devem reutilizar Identity, Permissions, Notifications, Documents, Mobility, Services e Wallet por contratos versionados.

## Arquitetura do MVP

### Aplicativo Android companheiro

O celular será a central principal para:

- vínculo entre usuário, responsável e dispositivo;
- configuração das cercas;
- geofencing;
- regras por data, horário e recorrência;
- notificações e escalonamento;
- sincronização com a API Health;
- armazenamento temporário offline;
- economia de bateria;
- visualização de histórico e incidentes.

### Aplicativo Wear OS

O relógio será responsável por:

- captura dos sinais oficialmente disponíveis;
- acompanhamento de exercícios;
- botão `Senti Agora`;
- alertas por vibração e interface simplificada;
- respostas `Estou bem`, `Estou acompanhado`, `Estou voltando` e `Preciso de ajuda`;
- localização de contingência quando possuir GPS e conectividade;
- aviso de bateria e perda de conexão;
- registros offline e sincronização posterior.

### Tecnologias iniciais

- Kotlin;
- Jetpack Compose;
- Jetpack Compose for Wear OS;
- Android Health Services;
- Health Connect;
- Android Data Layer API;
- APIs oficiais de localização e geofencing do Android;
- PostgreSQL e RabbitMQ já adotados pelo projeto;
- Docker local;
- Firebase Cloud Messaging dentro do nível gratuito;
- OpenStreetMap apenas quando necessário e sem API comercial obrigatória.

## Saúde e exercícios

O MVP deverá suportar, conforme capacidade real do dispositivo:

- frequência cardíaca;
- frequência cardíaca em repouso;
- passos, distância e atividade;
- sessões de treino;
- duração e zonas de esforço;
- histórico e linha de base pessoal;
- sono, oxigenação, temperatura, pressão e ECG somente quando oficialmente acessíveis e identificados pela origem;
- registro manual de sintomas;
- plano de cuidado e lembretes.

O sistema não diagnostica, não altera tratamento e não apresenta estimativa de smartwatch como medição clínica sem indicar claramente a origem.

## Telemedicina

O `Modo Consulta Viva` permitirá uma sessão temporária e consentida:

1. profissional solicita categorias de dados;
2. usuário aceita ou recusa cada categoria;
3. sistema verifica sensores disponíveis;
4. token temporário é emitido;
5. dados são transmitidos em tempo próximo do real;
6. painel informa origem, horário, qualidade, bateria e lacunas;
7. sessão expira automaticamente;
8. resumo é anexado ao prontuário somente mediante autorização.

A videoconferência permanece prioritariamente no celular, tablet ou computador. O relógio funciona como sensor companheiro.

## Health SafeZone

A SafeZone oferece proteção e acompanhamento legítimo para idosos, pessoas com demência ou desorientação, crianças, adolescentes sob responsabilidade legal e pessoas em recuperação.

### Regras suportadas

- cerca circular;
- cerca permanente;
- cerca temporária;
- cerca por data;
- cerca por horário;
- cerca recorrente;
- entrada e saída;
- tempo máximo de permanência;
- bateria baixa;
- dispositivo offline;
- confirmação de estado.

### Fase posterior

- corredor de rota;
- desvio persistente;
- não chegada;
- múltiplos responsáveis;
- rastreamento temporário durante incidente;
- escalonamento para círculo de cuidado.

### Fluxo de saída

1. detectar possível saída;
2. confirmar com nova leitura e margem de precisão;
3. alertar a pessoa acompanhada;
4. solicitar confirmação simples;
5. notificar o responsável;
6. elevar temporariamente a frequência de localização;
7. escalar para responsáveis secundários quando necessário;
8. encerrar ao retornar ou resolver o incidente.

## Privacidade e proteção contra abuso

Obrigatório:

- finalidade explícita;
- responsável identificado;
- vínculo legítimo e documentado;
- consentimento quando aplicável;
- controles próprios para menores e incapazes;
- indicação de acompanhamento ativo;
- revogação e expiração;
- trilha de acesso;
- bloqueio de rastreamento oculto;
- retenção mínima;
- criptografia;
- segregação por tenant;
- proibição de venda, publicidade comportamental ou compartilhamento indevido;
- mecanismo de denúncia e bloqueio por suspeita de abuso.

A localização detalhada deverá ser ativada apenas pela regra necessária ou durante incidente. Fora desses períodos, armazenar o mínimo indispensável.

## Entidades propostas

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
- `safe_routes`
- `route_waypoints`
- `location_samples`
- `location_incidents`
- `incident_escalations`
- `arrival_rules`
- `device_status_events`
- `guardian_notifications`
- `temporary_tracking_sessions`

## APIs planejadas

```http
POST   /v1/health/wearables/devices/link
DELETE /v1/health/wearables/devices/{device_id}/unlink
GET    /v1/health/wearables/devices/{device_id}/capabilities
POST   /v1/health/wearables/observations/batch
POST   /v1/health/wearables/workouts
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

## Eventos planejados

```text
health.wearable.device_linked.v1
health.observation.received.v1
health.workout.completed.v1
health.symptom.marked.v1
health.telemonitoring.session_started.v1
health.telemonitoring.session_completed.v1
health.safezone.created.v1
health.safezone.activated.v1
health.safezone.entered.v1
health.safezone.exited.v1
health.safezone.incident_opened.v1
health.safezone.incident_acknowledged.v1
health.safezone.incident_resolved.v1
health.safezone.device_battery_low.v1
health.safezone.device_offline.v1
```

## Limitações obrigatórias

O produto não promete localização perfeita, funcionamento sem bateria, detecção garantida, diagnóstico, prevenção de emergência, substituição de cuidador ou precisão hospitalar universal.

Toda interface de localização deverá mostrar último horário, precisão estimada, bateria, conectividade e origem da posição.

## Critérios de aceite arquitetural

- Android e Wear OS são as únicas plataformas do MVP;
- Apple permanece fora da primeira fase;
- nenhuma API paga é obrigatória para desenvolvimento;
- celular é a central de geofencing;
- relógio atua como sensor, alerta e contingência;
- dados sensíveis não aparecem em logs comuns;
- rastreamento ao vivo é temporário;
- o usuário sabe quando está sendo acompanhado;
- o recurso permanece dentro do módulo Health;
- Vision não é reintroduzido.
