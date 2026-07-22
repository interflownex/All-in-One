# `services.providers`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                                       |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:144 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:145 |
| category        | VARCHAR(100) | False | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:146 |
| approved_at     | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:147 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:148 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:149 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:150 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:151 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:152 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:153 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:154 |
| idempotency_key | VARCHAR(120) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:18                    |
