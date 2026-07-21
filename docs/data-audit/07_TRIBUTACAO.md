# Tributação e Perfis Fiscais

**Status:** proposta; implementação e homologação fiscal não comprovadas.

## Estruturas

Foram modeladas 5 estruturas fiscais e três estruturas de preço/custo. Regras possuem prioridade, jurisdição, regime, operação, cliente, destino, canal, benefício, alíquota, base, crédito, arredondamento, fundamento, vigência, versão e aprovação.

## Brasil

O checklist cobre `NCM`, `CEST`, `CFOP`, `CST`, `CSOSN`, `origem_mercadoria`, `ICMS`, `ICMS_ST`, `FCP`, `DIFAL`, `IPI`, `PIS`, `COFINS`, `ISS`, `CNAE`, `codigo_servico`, `retencoes`, `beneficios`, `ANP`, `GTIN`, `unidade_tributavel`, `quantidade_tributavel`, `valor_unitario_tributavel`. Aplicabilidade deve ser decidida por cenário e nunca duplicada indiscriminadamente em cada produto.

## Cálculo

Cada snapshot preserva regra, classificação, base, alíquota, valor, moeda, precisão, arredondamento, fundamento, versão e hash de entrada. Cálculos fiscais são exclusivos do backend.

## Gate

Migration, backfill, backend, frontend, testes e homologação fiscal permanecem não implementados.

EVIDÊNCIAS: `config/data_audit/product_units_tax_model_proposal.json`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.
