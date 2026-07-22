# `forms.form_submission_values`

| Campo             | Tipo        | Nulo  | PK    | FK                        | LGPD                             | Evidência                                                         |
| ----------------- | ----------- | ----- | ----- | ------------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                | UUID        | False | True  |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:290 |
| submission_id     | UUID        | False | False | forms.form_submissions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:291 |
| field_catalog_id  | UUID        | False | False | forms.field_catalog.id    | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:292 |
| data_type         | VARCHAR(40) | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:293 |
| normalized_value  | JSONB       | True  | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:294 |
| display_value     | TEXT        | True  | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:295 |
| unit              | VARCHAR(40) | True  | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:296 |
| source            | VARCHAR(30) | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:297 |
| validation_result | JSONB       | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:298 |
| sensitivity       | VARCHAR(40) | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:299 |
| encryption        | VARCHAR(40) | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:300 |
| schema_version    | INTEGER     | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:301 |
| created_at        | TIMESTAMPTZ | False | False |                           | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:302 |
