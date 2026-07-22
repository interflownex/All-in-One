# `stock.measurement_units`

| Campo                 | Tipo            | Nulo  | PK    | FK                         | LGPD                             | Evidência                                                    |
| --------------------- | --------------- | ----- | ----- | -------------------------- | -------------------------------- | ------------------------------------------------------------ |
| id                    | UUID            | False | True  |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:4  |
| code                  | VARCHAR(32)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:5  |
| symbol                | VARCHAR(24)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:6  |
| singular_name_pt_br   | VARCHAR(120)    | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:7  |
| plural_name_pt_br     | VARCHAR(120)    | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:8  |
| dimension             | VARCHAR(40)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:9  |
| measurement_system    | VARCHAR(40)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:10 |
| precision             | SMALLINT        | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:11 |
| scale                 | NUMERIC(30, 12) | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:12 |
| allows_fraction       | BOOLEAN         | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:13 |
| base_unit_id          | UUID            | True  | False | stock.measurement_units.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:14 |
| normative_equivalence | TEXT            | True  | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:15 |
| regional_rules        | JSONB           | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:16 |
| status                | VARCHAR(40)     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:17 |
| version               | INTEGER         | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:18 |
| created_at            | TIMESTAMPTZ     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:19 |
| created_by            | UUID            | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/025_units_tax_governance.sql:20 |
| updated_at            | TIMESTAMPTZ     | False | False |                            | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:21 |
| updated_by            | UUID            | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/025_units_tax_governance.sql:22 |
