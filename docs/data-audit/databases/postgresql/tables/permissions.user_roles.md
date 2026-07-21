# `permissions.user_roles`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:92 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:93 |
| role_id | UUID | False | False | permissions.roles.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:94 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:95 |
| valid_until | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:96 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:97 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:98 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:99 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:100 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:101 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:102 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:103 |
