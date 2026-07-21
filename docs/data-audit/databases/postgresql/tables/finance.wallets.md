# `finance.wallets`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:140 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:141 |
| wallet_type | VARCHAR(30) | False | False |  | financeiro confidencial | database/postgres/migrations/002_business_permissions_finance.sql:142 |
| brl_available | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:143 |
| brl_held | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:144 |
| nex_available | NUMERIC(18, 8) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:145 |
| nex_held | NUMERIC(18, 8) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:146 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:147 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:148 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:149 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:150 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:151 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:152 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:153 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/023_performance_indexes.sql:38 |
