# `permissions.approval_limits`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:122 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:123 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:124 |
| role_id | UUID | True | False | permissions.roles.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:125 |
| limit_brl | NUMERIC(18, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:126 |
| requires_dual_approval | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:127 |
| scope | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:128 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:129 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:130 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:131 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:132 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:133 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:134 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/002_business_permissions_finance.sql:135 |
