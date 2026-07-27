# Health

Pacientes, prontuario, consulta, telemedicina, prescricao, leitos, convenios, wearables e protecao SafeZone.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

Wearables e SafeZone sao capacidades internas do Health. Elas nao criam um
novo modulo e devem consumir Identity, Permissions, Notifications, Documents,
Mobility, Services e Wallet somente por contratos versionados.

## Entidades atuais

`patients`, `appointments`, `medical_records`, `prescriptions`, `beds`.

## Capacidades aprovadas

### Health Watch

- aplicativo companheiro Android;
- aplicativo nativo Wear OS;
- sinais disponibilizados oficialmente pelo dispositivo;
- exercicios e treinos;
- registro `Senti Agora`;
- telemonitoramento temporario e consentido;
- operacao offline com sincronizacao idempotente.

### Health SafeZone

- cerca circular;
- cerca permanente, temporaria e recorrente;
- regras por data e horario;
- alerta de entrada e saida;
- bateria baixa e dispositivo offline;
- confirmacao simples no relogio;
- localizacao temporaria durante incidente;
- protecao contra rastreamento oculto e abuso.

## Plataformas do MVP

- Android;
- Wear OS;
- Samsung, Xiaomi, Motorola e outros fabricantes quando o relogio utilizar
  Wear OS e disponibilizar os recursos necessarios.

Apple Watch e watchOS permanecem fora da primeira etapa por decisao economica.

## Prioridade

- `P0`: privacidade, vinculo, contratos, Android/Wear OS, cerca circular,
  incidentes, offline e testes.
- `P1`: saude, exercicios, experiencia familiar e pacote pre-consulta.
- `P2`: rotas seguras, nao chegada e Consulta Viva.
- `P3`: Apple, sistemas fechados e funcoes medicas reguladas.

Consulte:

- `docs/HEALTH_WATCH_SAFEZONE.md`;
- `docs/HEALTH_WATCH_SAFEZONE_PRIORITIES.md`.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
