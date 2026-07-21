# Unidades, Conversões, Precisão e Arredondamento

**Status:** implementação parcial comprovada; frontend, integração PostgreSQL viva e homologação pendentes.

## Estruturas

Foram modeladas 6 estruturas: `measurement_units`, `product_units`, `product_unit_conversions`, `stock_movements`, `product_lots`, `product_serials`. Os propósitos cobrem cadastro, estoque base, compra, venda, consumo, produção, transporte, fiscal, exibição, conferência e inventário.

## Conversão e precisão

- Decimal é obrigatório; ponto flutuante binário é proibido.
- Conversões exigem compatibilidade dimensional, vigência, versão, aprovação, tolerância e arredondamento.
- Conversões entre dimensões exigem fórmula segura, densidade e contexto técnico.
- Movimentações preservam unidade informada, quantidade base e snapshot do fator.
- O backend recalcula e registra correlação e idempotência.

## Gate

Migration reversível, rollback, estratégia de backfill sem inferência, cálculo Decimal e testes unitários estão implementados. Frontend, integração PostgreSQL viva e homologação permanecem pendentes. A migration não é aplicada por este documento.

EVIDÊNCIAS: `database/postgres/migrations/025_units_tax_governance.sql`, `database/postgres/rollbacks/025_units_tax_governance.down.sql`, `modules/shared/units_tax.py`, `tests/test_units_tax_governance.py`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.
