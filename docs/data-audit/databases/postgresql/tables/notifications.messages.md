# `notifications.messages`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:263 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:264 |
| channel | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:265 |
| template_key | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:266 |
| dispatched_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:267 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:268 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:269 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:270 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:271 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:272 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:273 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:274 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:77 |
