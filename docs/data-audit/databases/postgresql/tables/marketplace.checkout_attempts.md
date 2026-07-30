# `marketplace.checkout_attempts`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:4 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/032_marketplace_checkout_attempts.sql:5 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:6 |
| store_id | UUID | False | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:7 |
| cart_id | UUID | False | False | marketplace.carts.id | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:8 |
| order_id | UUID | False | False | marketplace.orders.id | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:9 |
| escrow_id | UUID | True | False | finance.escrows.id | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:10 |
| status | VARCHAR(48) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:11 |
| payment_status | VARCHAR(32) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:12 |
| payment_method | VARCHAR(32) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:13 |
| currency | CHAR(3) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:14 |
| expected_total_brl | NUMERIC(18, 2) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:15 |
| total_brl | NUMERIC(18, 2) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:16 |
| idempotency_key | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:17 |
| request_hash | CHAR(64) | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:18 |
| confirmation_idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:19 |
| confirmation_request_hash | CHAR(64) | True | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:20 |
| snapshot | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:21 |
| reservation_ids | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:22 |
| correlation_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:23 |
| causation_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:24 |
| expires_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:25 |
| confirmed_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:26 |
| cancelled_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:27 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:28 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:29 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/032_marketplace_checkout_attempts.sql:30 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/032_marketplace_checkout_attempts.sql:31 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/032_marketplace_checkout_attempts.sql:32 |
