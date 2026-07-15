# TMS

Transportadoras, frota, rotas, fretes, documentos e torre de controle.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`carriers`, `freights`, `routes`, `proofs_of_delivery`, `freight_audits`.

`freights` acompanha cotacao, despacho e conclusao; `proofs_of_delivery`
registra POD privado; `freight_audits` fecha a auditoria logistica.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
