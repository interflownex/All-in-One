# Vision

Dispositivos de camera, streams, gravacoes, deteccao e ocorrencias.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`devices`, `streams`, `recordings`, `motion_alerts`.

`streams` guarda somente metadados privados e hash da URL;
`recordings` preserva hash/storage append-only; `motion_alerts`
registra deteccoes e incidentes auditaveis.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
