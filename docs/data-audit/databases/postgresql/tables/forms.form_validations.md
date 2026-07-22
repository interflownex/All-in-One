# `forms.form_validations`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:179 |
| form_version_id | UUID | False | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:180 |
| field_id | UUID | True | False | forms.form_fields.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:181 |
| validation_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:182 |
| parameters | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:183 |
| message_pt_br | VARCHAR(300) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:184 |
| severity | VARCHAR(20) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:185 |
| condition | JSONB | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:186 |
| run_frontend | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:187 |
| run_backend | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:188 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:189 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:190 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:191 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:192 |
