# `stock.stock_movements`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:138 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:139 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:140 |
| branch_id | UUID | True | False | business.branches.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:141 |
| product_id | UUID | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:142 |
| variant_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:143 |
| lot_id | UUID | True | False | stock.product_lots.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:144 |
| serial_id | UUID | True | False | stock.product_serials.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:145 |
| source_location_id | UUID | True | False |  | dado pessoal | database/postgres/migrations/025_units_tax_governance.sql:146 |
| target_location_id | UUID | True | False |  | dado pessoal | database/postgres/migrations/025_units_tax_governance.sql:147 |
| movement_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:148 |
| informed_quantity | NUMERIC(30, 12) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:149 |
| informed_unit_id | UUID | False | False | stock.measurement_units.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:150 |
| base_quantity | NUMERIC(30, 12) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:151 |
| base_unit_id | UUID | False | False | stock.measurement_units.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:152 |
| conversion_id | UUID | True | False | stock.product_unit_conversions.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:153 |
| conversion_factor_snapshot | NUMERIC(30, 12) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:154 |
| previous_balance | NUMERIC(30, 12) | False | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:155 |
| new_balance | NUMERIC(30, 12) | False | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:156 |
| unit_cost | NUMERIC(30, 12) | True | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:157 |
| total_value | NUMERIC(30, 12) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:158 |
| currency_code | CHAR(3) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:159 |
| reason | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:160 |
| document_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:161 |
| order_id | UUID | True | False | marketplace.orders.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:162 |
| correlation_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:163 |
| idempotency_key | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:164 |
| occurred_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:165 |
| created_by | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:166 |
