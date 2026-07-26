# `forms.form_billing_events`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:307 |
| tenant_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:308 |
| form_definition_id | UUID | True | False | forms.form_definitions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:309 |
| form_version_id | UUID | True | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:310 |
| event_type | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:311 |
| occurred_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:312 |
| actor_user_id | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:313 |
| idempotency_key | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:314 |
| billing_reference | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:315 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:316 |
