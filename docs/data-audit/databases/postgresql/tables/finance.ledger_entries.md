# `finance.ledger_entries`

| Campo                | Tipo           | Nulo  | PK    | FK                | LGPD                             | Evidência                                                             |
| -------------------- | -------------- | ----- | ----- | ----------------- | -------------------------------- | --------------------------------------------------------------------- |
| id                   | UUID           | False | True  |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:158 |
| user_id              | UUID           | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:159 |
| wallet_id            | UUID           | False | False |                   | financeiro confidencial          | database/postgres/migrations/002_business_permissions_finance.sql:160 |
| counterparty_user_id | UUID           | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:161 |
| currency             | VARCHAR(10)    | False | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:162 |
| amount_brl           | NUMERIC(18, 4) | True  | False |                   | financeiro confidencial          | database/postgres/migrations/002_business_permissions_finance.sql:163 |
| amount_nex           | NUMERIC(18, 8) | True  | False |                   | financeiro confidencial          | database/postgres/migrations/002_business_permissions_finance.sql:164 |
| entry_type           | VARCHAR(40)    | False | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:165 |
| reference_type       | VARCHAR(60)    | True  | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:166 |
| reference_id         | UUID           | True  | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:167 |
| idempotency_key      | TEXT           | False | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:168 |
| status               | VARCHAR(40)    | False | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:169 |
| metadata             | JSONB          | False | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:170 |
| created_at           | TIMESTAMPTZ    | False | False |                   | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:171 |
| created_by           | UUID           | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/002_business_permissions_finance.sql:172 |
