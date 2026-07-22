# `forms.form_submissions`

| Campo              | Tipo         | Nulo  | PK    | FK                        | LGPD                             | Evidência                                                         |
| ------------------ | ------------ | ----- | ----- | ------------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                 | UUID         | False | True  |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:269 |
| form_definition_id | UUID         | False | False | forms.form_definitions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:270 |
| form_version_id    | UUID         | False | False | forms.form_versions.id    | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:271 |
| user_id            | UUID         | False | False | identity.users.id         | pseudônimo vinculável            | database/postgres/migrations/028_dynamic_forms_governance.sql:272 |
| tenant_id          | UUID         | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:273 |
| context            | JSONB        | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:274 |
| target_entity      | VARCHAR(120) | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:275 |
| target_entity_id   | UUID         | True  | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:276 |
| status             | VARCHAR(30)  | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:277 |
| started_at         | TIMESTAMPTZ  | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:278 |
| completed_at       | TIMESTAMPTZ  | True  | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:279 |
| source             | VARCHAR(30)  | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:280 |
| correlation_id     | UUID         | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:281 |
| idempotency_key    | VARCHAR(160) | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:282 |
| validation_result  | JSONB        | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:283 |
| audit_event_id     | UUID         | True  | False | audit.domain_events.id    | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:284 |
