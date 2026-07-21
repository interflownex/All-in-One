# `erp.product_tax_classifications`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:230 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:231 |
| product_id | UUID | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:232 |
| variant_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:233 |
| ncm | VARCHAR(10) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:234 |
| cest | VARCHAR(12) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:235 |
| origin_code | VARCHAR(4) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:236 |
| cst | VARCHAR(4) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:237 |
| csosn | VARCHAR(4) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:238 |
| service_code | VARCHAR(20) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:239 |
| cnae | VARCHAR(12) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:240 |
| anp_code | VARCHAR(20) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:241 |
| gtin | VARCHAR(18) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:242 |
| tax_unit_id | UUID | True | False | stock.measurement_units.id | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:243 |
| tax_quantity_rule | VARCHAR(500) | True | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:244 |
| effective_from | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:245 |
| effective_to | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:246 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:247 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:248 |
