# `permissions.access_policies`

| Campo      | Tipo        | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                             |
| ---------- | ----------- | ----- | ----- | --------------------- | -------------------------------- | --------------------------------------------------------------------- |
| id         | UUID        | False | True  |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:107 |
| user_id    | UUID        | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:108 |
| company_id | UUID        | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:109 |
| module     | VARCHAR(60) | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:110 |
| expression | JSONB       | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:111 |
| status     | VARCHAR(40) | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:112 |
| metadata   | JSONB       | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:113 |
| created_at | TIMESTAMPTZ | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:114 |
| updated_at | TIMESTAMPTZ | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:115 |
| deleted_at | TIMESTAMPTZ | True  | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:116 |
| created_by | UUID        | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:117 |
| updated_by | UUID        | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:118 |
