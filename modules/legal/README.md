# Legal

Processos, contratos, prazos, audiencias, provisionamento e alertas.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`cases`, `deadlines`, `hearings`, `legal_contracts`.

`cases` registra processo com tipo, abertura e risco; `deadlines`
acompanha prazo processual, alerta com MFA e conclusao auditavel.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
