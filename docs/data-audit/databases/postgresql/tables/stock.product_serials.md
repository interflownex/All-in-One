# `stock.product_serials`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:121 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:122 |
| product_id | UUID | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:123 |
| variant_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:124 |
| lot_id | UUID | True | False | stock.product_lots.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:125 |
| serial_number | VARCHAR(180) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:126 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:127 |
| location_id | UUID | True | False |  | dado pessoal | database/postgres/migrations/025_units_tax_governance.sql:128 |
| warranty_until | DATE | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:129 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:130 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:131 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:132 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:133 |
