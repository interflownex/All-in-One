# `marketplace.disputes`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:24 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/022_marketplace_disputes_support.sql:25 |
| order_id | UUID | False | False | marketplace.orders.id | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:26 |
| store_id | UUID | True | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:27 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:28 |
| offer_id | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:29 |
| case_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:30 |
| subject | VARCHAR(200) | True | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:31 |
| message | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:32 |
| desired_resolution | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:33 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:34 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:35 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:36 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:37 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/022_marketplace_disputes_support.sql:38 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/022_marketplace_disputes_support.sql:39 |
| idempotency_key | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:40 |
