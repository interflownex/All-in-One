# `forms.form_versions`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:72 |
| form_definition_id | UUID | False | False | forms.form_definitions.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:73 |
| version_number | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:74 |
| schema_version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:75 |
| status | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:76 |
| change_summary | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:77 |
| created_by | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:78 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:79 |
| submitted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:80 |
| submitted_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:81 |
| approved_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:82 |
| approved_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/028_dynamic_forms_governance.sql:83 |
| rejected_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:84 |
| rejected_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:85 |
| rejection_reason | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:86 |
| published_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:87 |
| published_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:88 |
| retired_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:89 |
| checksum | CHAR(64) | True | False |  | não classificado automaticamente | database/postgres/migrations/028_dynamic_forms_governance.sql:90 |
