# `forms.field_bindings`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:34 |
| field_catalog_id | UUID | False | False | forms.field_catalog.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:35 |
| command | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:36 |
| api | VARCHAR(240) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:37 |
| dto | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:38 |
| logical_path | VARCHAR(240) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:39 |
| data_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:40 |
| transformation | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:41 |
| version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:42 |
| validation_policy | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:43 |
| authorization_policy | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:44 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:45 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:46 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:47 |
