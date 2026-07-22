# `stock.product_lots`

| Campo             | Tipo         | Nulo  | PK    | FK                      | LGPD                             | Evidência                                                     |
| ----------------- | ------------ | ----- | ----- | ----------------------- | -------------------------------- | ------------------------------------------------------------- |
| id                | UUID         | False | True  |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:94  |
| tenant_id         | UUID         | False | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:95  |
| company_id        | UUID         | True  | False | business.companies.id   | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:96  |
| product_id        | UUID         | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:97  |
| variant_id        | UUID         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:98  |
| lot_number        | VARCHAR(120) | False | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:99  |
| sub_lot           | VARCHAR(120) | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:100 |
| manufactured_on   | DATE         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:101 |
| expires_on        | DATE         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:102 |
| received_at       | TIMESTAMPTZ  | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:103 |
| supplier_id       | UUID         | True  | False | stock.suppliers.id      | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:104 |
| origin            | VARCHAR(160) | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:105 |
| quality_status    | VARCHAR(40)  | False | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:106 |
| inspection_id     | UUID         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:107 |
| quarantine_reason | TEXT         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:108 |
| released_at       | TIMESTAMPTZ  | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:109 |
| blocked_at        | TIMESTAMPTZ  | True  | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:110 |
| recall_status     | VARCHAR(40)  | False | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:111 |
| cost_method       | VARCHAR(40)  | False | False |                         | financeiro confidencial          | database/postgres/migrations/025_units_tax_governance.sql:112 |
| status            | VARCHAR(40)  | False | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:113 |
| created_at        | TIMESTAMPTZ  | False | False |                         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:114 |
| created_by        | UUID         | True  | False | identity.users.id       | pseudônimo vinculável            | database/postgres/migrations/025_units_tax_governance.sql:115 |
