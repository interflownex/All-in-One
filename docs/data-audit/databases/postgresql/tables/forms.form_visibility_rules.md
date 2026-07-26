# `forms.form_visibility_rules`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:197 |
| form_version_id | UUID | False | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:198 |
| target_type | VARCHAR(20) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:199 |
| target_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:200 |
| condition | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:201 |
| operator | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:202 |
| comparison_value | JSONB | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:203 |
| result | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:204 |
| priority | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:205 |
| combination | VARCHAR(10) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:206 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:207 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:208 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:209 |
