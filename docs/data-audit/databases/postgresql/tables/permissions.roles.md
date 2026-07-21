# `permissions.roles`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:62 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:63 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:64 |
| name | VARCHAR(80) | False | False |  | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:65 |
| is_system | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:66 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:67 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:68 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:69 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:70 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:71 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:72 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:73 |
