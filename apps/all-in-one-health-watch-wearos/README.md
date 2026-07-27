# All in One Health Watch Wear OS

Aplicativo nativo Wear OS do modulo Health.

## Prioridade

`P0_CRITICA`

## Responsabilidades

- vincular o relogio ao aplicativo Android companheiro;
- identificar capacidades reais do dispositivo;
- coletar sinais oficialmente acessiveis;
- acompanhar exercicios;
- registrar `Senti Agora`;
- receber alertas SafeZone;
- permitir respostas simples;
- acionar pedido de ajuda;
- informar bateria, conectividade e perda de vinculo;
- operar como localizacao de contingencia quando houver GPS e conexao;
- armazenar eventos offline e sincronizar posteriormente.

## Stack aprovada

- Kotlin;
- Jetpack Compose for Wear OS;
- Android Health Services;
- Data Layer API;
- APIs oficiais de sensores e localizacao;
- instalacao local por ADB durante desenvolvimento.

## Respostas de incidente

- `Estou bem`;
- `Estou acompanhado`;
- `Estou voltando`;
- `Preciso de ajuda`.

## Regras obrigatorias

- nao prometer sensor indisponivel;
- exibir origem e horario dos dados;
- nao diagnosticar;
- nao esconder acompanhamento ativo;
- economizar bateria;
- aumentar frequencia de localizacao apenas durante incidente;
- reduzir frequencia automaticamente apos resolucao;
- preservar dados sensiveis fora de logs comuns.

## Primeiro incremento executavel

1. projeto Wear OS compilavel;
2. tela de vinculo;
3. perfil de capacidades;
4. status de bateria e conexao;
5. recebimento de alerta SafeZone;
6. confirmacao simples;
7. registro offline;
8. sincronizacao com o companion Android;
9. testes em emulador e dispositivo fisico.

Consulte `docs/HEALTH_WATCH_SAFEZONE.md` e
`docs/HEALTH_WATCH_SAFEZONE_PRIORITIES.md`.
