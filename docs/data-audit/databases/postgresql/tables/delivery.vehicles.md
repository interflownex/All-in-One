# `delivery.vehicles`

| Campo            | Tipo           | Nulo  | PK    | FK                         | LGPD                             | Evidência                                                                      |
| ---------------- | -------------- | ----- | ----- | -------------------------- | -------------------------------- | ------------------------------------------------------------------------------ |
| id               | UUID           | False | True  |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:23 |
| user_id          | UUID           | False | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:24 |
| rider_profile_id | UUID           | False | False | delivery.rider_profiles.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:25 |
| type             | VARCHAR(40)    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:26 |
| license_plate    | VARCHAR(12)    | True  | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:27 |
| capacity_kg      | NUMERIC(12, 3) | True  | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:28 |
| refrigerated     | BOOLEAN        | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:29 |
| approved_at      | TIMESTAMPTZ    | True  | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:30 |
| status           | VARCHAR(40)    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:31 |
| metadata         | JSONB          | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:32 |
| created_at       | TIMESTAMPTZ    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:33 |
| updated_at       | TIMESTAMPTZ    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:34 |
| deleted_at       | TIMESTAMPTZ    | True  | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:35 |
| created_by       | UUID           | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:36 |
| updated_by       | UUID           | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:37 |
| idempotency_key  | VARCHAR(120)   | True  | False |                            | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:14                   |
