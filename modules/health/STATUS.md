# Status: Health

- Estado: `domain_engine_active`
- Runtime: FastAPI com persistencia SQLite contratual, autorizacao, auditoria e outbox
- Contrato: publicado localmente em `OPENAPI.yaml` e `CONTRACT.md`
- Persistencia: schema e tabelas iniciais cobertos por migracoes
- Novo incremento aprovado: `Health Watch + SafeZone`
- Plataformas do MVP: `Android + Wear OS`
- Apple/watchOS: `fora_da_primeira_etapa`
- Restricao economica: desenvolvimento inicial sem dependencia obrigatoria de API, licenca ou infraestrutura paga
- Prioridade atual: `P0_CRITICA`

## P0 — Proximo incremento obrigatorio

1. privacidade, consentimento, vinculo de cuidado e protecao antiabuso;
2. vinculo seguro entre All-in-One ID, celular e smartwatch;
3. contratos e modelo de dados para wearables, cercas e incidentes;
4. scaffold dos aplicativos Android companheiro e Wear OS;
5. cerca circular por data, horario e recorrencia;
6. alertas de saida, bateria baixa e dispositivo offline;
7. operacao offline, sincronizacao idempotente e auditoria;
8. testes de precisao, falsos positivos, revogacao e perda de conexao.

## Dependencias posteriores

- `P1`: sinais, treinos, Senti Agora, historico e experiencia familiar;
- `P2`: rotas seguras, nao chegada, circulo de cuidado e Consulta Viva;
- `P3`: Apple, sistemas fechados, sensores proprietarios e funcoes medicas reguladas.

Consulte `docs/HEALTH_WATCH_SAFEZONE.md` e
`docs/HEALTH_WATCH_SAFEZONE_PRIORITIES.md`.
