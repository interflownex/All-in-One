# `forms.form_homologations`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:235 |
| form_version_id | UUID | False | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:236 |
| requester_id | UUID | False | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:237 |
| requested_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:238 |
| checklist | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:239 |
| result | VARCHAR(30) | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:240 |
| reviewer_id | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:241 |
| reviewed_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:242 |
| notes | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:243 |
| problems | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:244 |
| corrections | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:245 |
| revalidation | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:246 |
| evidence | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:247 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:248 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:249 |
