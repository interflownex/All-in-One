# `permissions.permissions`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:77 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:78 |
| module | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:79 |
| action | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:80 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:81 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:82 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:83 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:84 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:85 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:86 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:87 |
