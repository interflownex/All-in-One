# STOCK

Catálogo curado de fornecedores homologados, sem estoque físico próprio, com pedido sob demanda, regras de preço, tracking e descontos por Pepitas. Entra na primeira etapa com AliExpress e CJ Dropshipping como fontes iniciais, sob operação controlada e expansão condicionada à qualidade.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`suppliers`, `catalog_products`, `price_rules`, `supplier_orders`, `discount_quotes`.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
