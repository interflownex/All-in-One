# `erp.tax_calculation_snapshots`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:276 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:277 |
| document_id | UUID | False | False | erp.fiscal_documents.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:278 |
| item_id | UUID | True | False | erp.invoice_items.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:279 |
| rule_id | UUID | False | False | erp.fiscal_rules.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:280 |
| classification_id | UUID | False | False | erp.product_tax_classifications.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:281 |
| tax_type | VARCHAR(32) | False | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:282 |
| tax_base | NUMERIC(30, 12) | False | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:283 |
| rate | NUMERIC(12, 8) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:284 |
| tax_amount | NUMERIC(30, 12) | False | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:285 |
| currency_code | CHAR(3) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:286 |
| precision | SMALLINT | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:287 |
| rounding_mode | VARCHAR(24) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:288 |
| legal_basis | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:289 |
| calculated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:290 |
| calculation_version | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:291 |
| input_hash | VARCHAR(128) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:292 |
| created_by | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:293 |
