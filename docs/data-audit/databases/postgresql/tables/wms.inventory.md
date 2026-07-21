# `wms.inventory`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:35 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:36 |
| warehouse_id | UUID | False | False | wms.warehouses.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:37 |
| sku | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:38 |
| bin_code | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:39 |
| quantity | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:40 |
| lot_code | VARCHAR(80) | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:41 |
| expires_at | DATE | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:42 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:43 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:44 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:45 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:46 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:47 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:48 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:49 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:30 |
