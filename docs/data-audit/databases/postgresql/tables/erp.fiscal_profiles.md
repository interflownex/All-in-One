# `erp.fiscal_profiles`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:171 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:172 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:173 |
| name | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:174 |
| country_code | CHAR(2) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:175 |
| tax_regime | VARCHAR(80) | False | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:176 |
| jurisdiction_scope | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:177 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:178 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:179 |
| effective_from | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:180 |
| effective_to | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:181 |
| approved_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:182 |
| approved_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:183 |
