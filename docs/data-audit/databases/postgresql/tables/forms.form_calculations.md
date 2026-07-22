# `forms.form_calculations`

| Campo                     | Tipo         | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                         |
| ------------------------- | ------------ | ----- | ----- | ---------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                        | UUID         | False | True  |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:152 |
| form_version_id           | UUID         | False | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:153 |
| name                      | VARCHAR(120) | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:154 |
| result_field_id           | UUID         | False | False | forms.form_fields.id   | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:155 |
| operand_field_ids         | JSONB        | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:156 |
| operation                 | VARCHAR(40)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:157 |
| safe_expression           | JSONB        | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:158 |
| display_order             | INTEGER      | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:159 |
| precision                 | SMALLINT     | True  | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:160 |
| rounding                  | VARCHAR(20)  | True  | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:161 |
| trigger_mode              | VARCHAR(30)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:162 |
| condition                 | JSONB        | True  | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:163 |
| unit                      | VARCHAR(40)  | True  | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:164 |
| null_handling             | VARCHAR(30)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:165 |
| division_by_zero_handling | VARCHAR(30)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:166 |
| visibility                | VARCHAR(30)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:167 |
| validation                | JSONB        | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:168 |
| status                    | VARCHAR(30)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:169 |
| version                   | INTEGER      | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:170 |
| created_at                | TIMESTAMPTZ  | False | False |                        | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:171 |
| created_by                | UUID         | True  | False | identity.users.id      | pseudônimo vinculável            | database/postgres/migrations/028_dynamic_forms_governance.sql:172 |
