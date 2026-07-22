# `forms.form_blocks`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:103 |
| form_version_id | UUID | False | False | forms.form_versions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:104 |
| block_type | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:105 |
| parent_block_id | UUID | True | False | forms.form_blocks.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:106 |
| display_order | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:107 |
| title | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:108 |
| description | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:109 |
| width | SMALLINT | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:110 |
| collapsible | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:111 |
| visibility_rule_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:112 |
| repeatable | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:113 |
| allowed_style | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:114 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:115 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:116 |
