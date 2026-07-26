# `erp.product_fiscal_assignments`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:254 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:255 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:256 |
| branch_id | UUID | True | False | business.branches.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:257 |
| product_id | UUID | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:258 |
| variant_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:259 |
| fiscal_profile_id | UUID | False | False | erp.fiscal_profiles.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:260 |
| classification_id | UUID | False | False | erp.product_tax_classifications.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:261 |
| exception_rule_id | UUID | True | False | erp.fiscal_rules.id | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:262 |
| effective_from | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:263 |
| effective_to | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:264 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:265 |
| approved_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/025_units_tax_governance.sql:266 |
| approved_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/025_units_tax_governance.sql:267 |
