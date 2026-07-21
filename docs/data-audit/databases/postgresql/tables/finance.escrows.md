# `finance.escrows`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:179 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:180 |
| wallet_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:181 |
| beneficiary_user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:182 |
| amount_brl | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:183 |
| release_condition | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:184 |
| dispute_deadline | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:185 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:186 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:187 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:188 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:189 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:190 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:191 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:192 |
