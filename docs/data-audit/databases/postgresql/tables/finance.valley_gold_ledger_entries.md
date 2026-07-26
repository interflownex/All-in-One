# `finance.valley_gold_ledger_entries`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:4 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/015_valley_gold_ledger.sql:5 |
| merchant_business_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:6 |
| entry_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:7 |
| amount_gold_delta | INTEGER | False | False |  | financeiro confidencial | database/postgres/migrations/015_valley_gold_ledger.sql:8 |
| reference_type | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:9 |
| reference_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:10 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:11 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:12 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:13 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/015_valley_gold_ledger.sql:14 |
| idempotency_key | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/015_valley_gold_ledger.sql:15 |
