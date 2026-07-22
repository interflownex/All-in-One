# `vision.devices`

| Campo              | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| ------------------ | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id                 | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:200 |
| user_id            | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:201 |
| device_fingerprint | TEXT         | False | False |                   | dado pessoal                     | database/postgres/migrations/004_enterprise_verticals.sql:202 |
| location_label     | VARCHAR(160) | True  | False |                   | dado pessoal                     | database/postgres/migrations/004_enterprise_verticals.sql:203 |
| retention_days     | INTEGER      | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:204 |
| status             | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:205 |
| metadata           | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:206 |
| created_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:207 |
| updated_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:208 |
| deleted_at         | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:209 |
| created_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:210 |
| updated_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:211 |
| idempotency_key    | VARCHAR(120) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:62  |
