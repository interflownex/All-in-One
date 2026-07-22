# `tms.freights`

| Campo             | Tipo           | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                    |
| ----------------- | -------------- | ----- | ----- | --------------------- | -------------------------------- | ------------------------------------------------------------ |
| id                | UUID           | False | True  |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:53 |
| user_id           | UUID           | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:54 |
| company_id        | UUID           | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:55 |
| driver_user_id    | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:56 |
| freight_brl       | NUMERIC(18, 4) | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:57 |
| toll_brl          | NUMERIC(18, 4) | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:58 |
| proof_of_delivery | JSONB          | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:59 |
| status            | VARCHAR(40)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:60 |
| metadata          | JSONB          | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:61 |
| created_at        | TIMESTAMPTZ    | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:62 |
| updated_at        | TIMESTAMPTZ    | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:63 |
| deleted_at        | TIMESTAMPTZ    | True  | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:64 |
| created_by        | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:65 |
| updated_by        | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:66 |
| idempotency_key   | VARCHAR(120)   | True  | False |                       | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:33 |
