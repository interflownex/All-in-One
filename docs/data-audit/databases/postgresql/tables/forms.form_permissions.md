# `forms.form_permissions`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:216 |
| form_definition_id | UUID | False | False | forms.form_definitions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:217 |
| form_version_id | UUID | True | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:218 |
| role | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:219 |
| attribute_condition | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:220 |
| can_view | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:221 |
| can_create | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:222 |
| can_edit | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:223 |
| can_approve | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:224 |
| can_publish | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:225 |
| can_export | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:226 |
| can_print | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:227 |
| can_access_sensitive | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:228 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:229 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:230 |
