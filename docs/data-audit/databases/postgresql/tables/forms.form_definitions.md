# `forms.form_definitions`

| Campo              | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                        |
| ------------------ | ------------ | ----- | ----- | --------------------- | -------------------------------- | ---------------------------------------------------------------- |
| id                 | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:54 |
| tenant_id          | UUID         | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:55 |
| company_id         | UUID         | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:56 |
| module_id          | VARCHAR(80)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:57 |
| business_context   | VARCHAR(120) | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:58 |
| name               | VARCHAR(160) | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:59 |
| description        | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:60 |
| status             | VARCHAR(30)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:61 |
| current_version_id | UUID         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:62 |
| created_by         | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/028_dynamic_forms_governance.sql:63 |
| created_at         | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:64 |
| updated_by         | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/028_dynamic_forms_governance.sql:65 |
| updated_at         | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:66 |
| deleted_at         | TIMESTAMPTZ  | True  | False |                       | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:67 |
