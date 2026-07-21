# `marketplace.pepita_grants`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:4 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/014_valley_ecosystem.sql:5 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:6 |
| order_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:7 |
| customer_user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/014_valley_ecosystem.sql:8 |
| pepitas | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:9 |
| merchant_gold_ledger_id | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:10 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:11 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:12 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:13 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:14 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:15 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/014_valley_ecosystem.sql:16 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/014_valley_ecosystem.sql:17 |
| idempotency_key | VARCHAR(100) | True | False |  | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:18 |
