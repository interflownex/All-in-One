# `identity.led_cards`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:198 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:199 |
| wallet_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:200 |
| card_uid_hash | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:201 |
| nfc_public_token_hash | TEXT | True | False |  | sensível/restrito | database/postgres/migrations/002_business_permissions_finance.sql:202 |
| activated_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:203 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:204 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:205 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:206 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:207 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:208 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:209 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:210 |
