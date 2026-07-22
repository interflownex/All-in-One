# `business.user_company_memberships`

| Campo           | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                            |
| --------------- | ------------ | ----- | ----- | --------------------- | -------------------------------- | -------------------------------------------------------------------- |
| id              | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:46 |
| user_id         | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:47 |
| company_id      | UUID         | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:48 |
| department      | VARCHAR(100) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:49 |
| cost_center     | VARCHAR(100) | True  | False |                       | financeiro confidencial          | database/postgres/migrations/002_business_permissions_finance.sql:50 |
| status          | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:51 |
| metadata        | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:52 |
| created_at      | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:53 |
| updated_at      | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:54 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:55 |
| created_by      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:56 |
| updated_by      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:57 |
| idempotency_key | VARCHAR(120) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/011_business_idempotency.sql:5          |
