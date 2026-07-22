# `forms.form_publications`

| Campo               | Tipo        | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                         |
| ------------------- | ----------- | ----- | ----- | ---------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                  | UUID        | False | True  |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:254 |
| form_version_id     | UUID        | False | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:255 |
| environment         | VARCHAR(30) | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:256 |
| published_at        | TIMESTAMPTZ | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:257 |
| published_by        | UUID        | False | False | identity.users.id      | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:258 |
| rollout_policy      | JSONB       | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:259 |
| rollback_version_id | UUID        | True  | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:260 |
| tenant_scope        | JSONB       | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:261 |
| channels            | JSONB       | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:262 |
| checksum            | CHAR(64)    | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:263 |
| status              | VARCHAR(30) | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:264 |
