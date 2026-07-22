# `stock.product_unit_conversions`

| Campo                 | Tipo            | Nulo  | PK    | FK                         | LGPD                             | Evidência                                                    |
| --------------------- | --------------- | ----- | ----- | -------------------------- | -------------------------------- | ------------------------------------------------------------ |
| id                    | UUID            | False | True  |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:57 |
| tenant_id             | UUID            | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:58 |
| company_id            | UUID            | True  | False | business.companies.id      | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:59 |
| branch_id             | UUID            | True  | False | business.branches.id       | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:60 |
| product_id            | UUID            | False | False | marketplace.products.id    | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:61 |
| variant_id            | UUID            | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:62 |
| source_unit_id        | UUID            | False | False | stock.measurement_units.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:63 |
| target_unit_id        | UUID            | False | False | stock.measurement_units.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:64 |
| multiplier            | NUMERIC(30, 12) | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:65 |
| divisor               | NUMERIC(30, 12) | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:66 |
| safe_formula          | VARCHAR(500)    | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:67 |
| precision             | SMALLINT        | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:68 |
| rounding_mode         | VARCHAR(24)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:69 |
| tolerance             | NUMERIC(30, 12) | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:70 |
| effective_from        | TIMESTAMPTZ     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:71 |
| effective_to          | TIMESTAMPTZ     | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:72 |
| context               | VARCHAR(80)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:73 |
| supplier_id           | UUID            | True  | False | stock.suppliers.id         | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:74 |
| package_id            | UUID            | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:75 |
| density               | NUMERIC(30, 12) | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:76 |
| reference_temperature | NUMERIC(12, 4)  | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:77 |
| status                | VARCHAR(40)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:78 |
| version               | INTEGER         | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:79 |
| approved_at           | TIMESTAMPTZ     | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:80 |
| approved_by           | UUID            | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/025_units_tax_governance.sql:81 |
| created_at            | TIMESTAMPTZ     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:82 |
| created_by            | UUID            | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/025_units_tax_governance.sql:83 |
