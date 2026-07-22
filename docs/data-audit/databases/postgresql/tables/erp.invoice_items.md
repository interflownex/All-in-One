# `erp.invoice_items`

| Campo              | Tipo           | Nulo  | PK    | FK                      | LGPD                             | Evidência                                                 |
| ------------------ | -------------- | ----- | ----- | ----------------------- | -------------------------------- | --------------------------------------------------------- |
| id                 | UUID           | False | True  |                         | não classificado automaticamente | database/postgres/migrations/017_erp_invoice_items.sql:5  |
| fiscal_document_id | UUID           | False | False | erp.fiscal_documents.id | não classificado automaticamente | database/postgres/migrations/017_erp_invoice_items.sql:6  |
| description        | TEXT           | False | False |                         | não classificado automaticamente | database/postgres/migrations/017_erp_invoice_items.sql:7  |
| quantity           | NUMERIC(18, 4) | False | False |                         | não classificado automaticamente | database/postgres/migrations/017_erp_invoice_items.sql:8  |
| unit_price_brl     | NUMERIC(18, 4) | False | False |                         | financeiro confidencial          | database/postgres/migrations/017_erp_invoice_items.sql:9  |
| total_price_brl    | NUMERIC(18, 4) | False | False |                         | financeiro confidencial          | database/postgres/migrations/017_erp_invoice_items.sql:10 |
| tax_amount_brl     | NUMERIC(18, 4) | False | False |                         | financeiro confidencial          | database/postgres/migrations/017_erp_invoice_items.sql:11 |
| created_at         | TIMESTAMPTZ    | False | False |                         | não classificado automaticamente | database/postgres/migrations/017_erp_invoice_items.sql:12 |
| updated_at         | TIMESTAMPTZ    | False | False |                         | não classificado automaticamente | database/postgres/migrations/017_erp_invoice_items.sql:13 |
