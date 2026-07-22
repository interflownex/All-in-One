# `business.company_documents`

| Campo           | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                            |
| --------------- | ------------ | ----- | ----- | --------------------- | -------------------------------- | -------------------------------------------------------------------- |
| id              | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:30 |
| user_id         | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:31 |
| company_id      | UUID         | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:32 |
| document_type   | VARCHAR(80)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:33 |
| storage_key     | TEXT         | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:34 |
| expires_at      | DATE         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:35 |
| status          | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:36 |
| metadata        | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:37 |
| created_at      | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:38 |
| updated_at      | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:39 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                       | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:40 |
| created_by      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:41 |
| updated_by      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:42 |
| idempotency_key | VARCHAR(120) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/011_business_idempotency.sql:4          |
