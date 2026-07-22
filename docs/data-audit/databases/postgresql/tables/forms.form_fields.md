# `forms.form_fields`

| Campo              | Tipo         | Nulo  | PK    | FK                      | LGPD                             | Evidência                                                         |
| ------------------ | ------------ | ----- | ----- | ----------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                 | UUID         | False | True  |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:121 |
| form_version_id    | UUID         | False | False | forms.form_versions.id  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:122 |
| block_id           | UUID         | False | False | forms.form_blocks.id    | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:123 |
| field_catalog_id   | UUID         | False | False | forms.field_catalog.id  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:124 |
| field_binding_id   | UUID         | False | False | forms.field_bindings.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:125 |
| component          | VARCHAR(40)  | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:126 |
| label              | VARCHAR(160) | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:127 |
| help_text          | TEXT         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:128 |
| placeholder        | VARCHAR(240) | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:129 |
| required           | BOOLEAN      | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:130 |
| read_only          | BOOLEAN      | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:131 |
| hidden             | BOOLEAN      | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:132 |
| display_order      | INTEGER      | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:133 |
| width              | SMALLINT     | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:134 |
| mask               | VARCHAR(80)  | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:135 |
| format             | VARCHAR(80)  | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:136 |
| default_value      | JSONB        | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:137 |
| value_source       | VARCHAR(40)  | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:138 |
| unit               | VARCHAR(40)  | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:139 |
| permissions        | JSONB        | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:140 |
| visibility_rule_id | UUID         | True  | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:141 |
| validation_ids     | JSONB        | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:142 |
| audit_policy       | JSONB        | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:143 |
| created_at         | TIMESTAMPTZ  | False | False |                         | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:144 |
| created_by         | UUID         | True  | False | identity.users.id       | pseudônimo vinculável            | database/postgres/migrations/028_dynamic_forms_governance.sql:145 |
