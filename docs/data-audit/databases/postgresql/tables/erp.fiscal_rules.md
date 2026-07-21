# `erp.fiscal_rules`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:189 |
| fiscal_profile_id | UUID | False | False | erp.fiscal_profiles.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:190 |
| priority | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:191 |
| country_code | CHAR(2) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:192 |
| state_code | CHAR(2) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:193 |
| city_code | VARCHAR(12) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:194 |
| operation_nature | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:195 |
| customer_type | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:196 |
| taxpayer_status | VARCHAR(40) | True | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:197 |
| destination_type | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:198 |
| channel | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:199 |
| product_type | VARCHAR(60) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:200 |
| purpose | VARCHAR(60) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:201 |
| tax_benefit | VARCHAR(120) | True | False |  | financeiro confidencial | database/postgres/migrations/025_units_tax_governance.sql:202 |
| substitution | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:203 |
| single_phase | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:204 |
| withholding | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:205 |
| exemption | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:206 |
| immunity | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:207 |
| deferral | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:208 |
| base_reduction | NUMERIC(9, 6) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:209 |
| rate | NUMERIC(12, 8) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:210 |
| base_formula | VARCHAR(500) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:211 |
| credit_rule | VARCHAR(500) | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:212 |
| rounding_mode | VARCHAR(24) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:213 |
| legal_basis | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:214 |
| effective_from | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:215 |
| effective_to | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:216 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:217 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:218 |
| approved_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:219 |
| approved_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:220 |
