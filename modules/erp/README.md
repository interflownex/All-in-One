# ERP

Financeiro empresarial, compras, vendas, fiscal, controladoria e aprovacao.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`accounts`, `payables`, `receivables`, `cost_centers`, `fiscal_documents`.

`payables` e `receivables` registram contas financeiras com centro
de custo/conta contabil, aprovacao de pagamento e conciliacao MFA.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
