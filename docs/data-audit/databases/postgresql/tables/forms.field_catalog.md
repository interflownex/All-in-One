# `forms.field_catalog`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:6 |
| domain | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:7 |
| logical_entity | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:8 |
| logical_field | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:9 |
| data_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:10 |
| description | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:11 |
| allowed_components | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:12 |
| mandatory_validations | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:13 |
| sensitivity | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:14 |
| permissions | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:15 |
| authorized_binding | VARCHAR(240) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:16 |
| allowed_operations | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:17 |
| allowed_calculations | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:18 |
| unit | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:19 |
| format | VARCHAR(80) | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:20 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:21 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:22 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:23 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:24 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:25 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:26 |
