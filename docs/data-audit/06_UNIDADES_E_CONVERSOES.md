# Unidades, Conversões, Precisão e Arredondamento

**Status:** proposta; implementação não comprovada.

## Estruturas

Foram modeladas 6 estruturas: `measurement_units`, `product_units`, `product_unit_conversions`, `stock_movements`, `product_lots`, `product_serials`. Os propósitos cobrem cadastro, estoque base, compra, venda, consumo, produção, transporte, fiscal, exibição, conferência e inventário.

## Conversão e precisão

- Decimal é obrigatório; ponto flutuante binário é proibido.
- Conversões exigem compatibilidade dimensional, vigência, versão, aprovação, tolerância e arredondamento.
- Conversões entre dimensões exigem fórmula segura, densidade e contexto técnico.
- Movimentações preservam unidade informada, quantidade base e snapshot do fator.
- O backend recalcula e registra correlação e idempotência.

## Gate

Migration, backfill, backend, frontend e testes permanecem não implementados. Nenhuma migration é aplicada por este documento.

EVIDÊNCIAS: `config/data_audit/product_units_tax_model_proposal.json`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.
