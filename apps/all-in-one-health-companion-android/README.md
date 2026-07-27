# All in One Health Companion Android

Aplicativo Android companheiro do Health Watch e central principal da SafeZone.

## Prioridade

`P0_CRITICA`

## Responsabilidades

- autenticar e vincular usuario, dependente, responsavel e dispositivo;
- configurar cercas permanentes, temporarias, por data, horario e recorrencia;
- executar geofencing com APIs oficiais do Android;
- sincronizar sinais, treinos, sintomas e incidentes com o modulo Health;
- armazenar eventos temporariamente quando offline;
- receber e apresentar alertas;
- controlar responsaveis e consentimentos;
- exibir precisao, horario, bateria e conectividade;
- impedir rastreamento oculto ou sem vinculo legitimo.

## Stack aprovada

- Kotlin;
- Jetpack Compose;
- Health Connect;
- Android Health Services por integracao com Wear OS;
- Data Layer API;
- APIs oficiais de geofencing e localizacao;
- Firebase Cloud Messaging no nivel gratuito;
- OpenStreetMap apenas quando necessario.

## Fora do escopo inicial

- Apple/iOS;
- APIs pagas de mapas;
- SMS pago;
- rastreamento permanente de alta frequencia;
- diagnostico ou decisao medica autonoma.

## Primeiro incremento executavel

1. projeto Android compilavel;
2. tela de vinculo;
3. consentimento e responsavel principal;
4. cadastro de cerca circular;
5. monitor de geofence;
6. notificacao de saida;
7. confirmacao e encerramento de incidente;
8. fila offline e sincronizacao idempotente;
9. testes unitarios e instrumentados.

Consulte `docs/HEALTH_WATCH_SAFEZONE.md` e
`docs/HEALTH_WATCH_SAFEZONE_PRIORITIES.md`.
