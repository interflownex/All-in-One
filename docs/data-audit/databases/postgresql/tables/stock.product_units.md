# `stock.product_units`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:27 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:28 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:29 |
| product_id | UUID | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:30 |
| variant_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:31 |
| unit_id | UUID | False | False | stock.measurement_units.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:32 |
| purpose | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:33 |
| is_default | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:34 |
| minimum_quantity | NUMERIC(30, 12) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:35 |
| maximum_quantity | NUMERIC(30, 12) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:36 |
| quantity_step | NUMERIC(30, 12) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:37 |
| precision | SMALLINT | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:38 |
| rounding_mode | VARCHAR(24) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:39 |
| effective_from | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:40 |
| effective_to | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:41 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:42 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:43 |
| approved_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:44 |
| approved_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:45 |
