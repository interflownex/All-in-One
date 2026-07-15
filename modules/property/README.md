# Property

Imoveis, unidades, locacoes, condominio, manutencao e votacao.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`properties`, `units`, `leases`, `assemblies`, `maintenance_orders`.

`leases` acompanha locacoes com aluguel auditavel; `maintenance_orders`
registra solicitacao, agenda e conclusao de manutencao com MFA.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
