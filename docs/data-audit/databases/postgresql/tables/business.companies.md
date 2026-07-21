# `business.companies`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:4 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:5 |
| parent_company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:6 |
| cnpj | VARCHAR(18) | False | False |  | sensível/restrito | database/postgres/migrations/002_business_permissions_finance.sql:7 |
| root_cnpj | VARCHAR(18) | False | False |  | sensível/restrito | database/postgres/migrations/002_business_permissions_finance.sql:8 |
| legal_name | VARCHAR(240) | False | False |  | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:9 |
| trade_name | VARCHAR(240) | True | False |  | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:10 |
| cnae | VARCHAR(20) | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:11 |
| state_registration | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:12 |
| municipal_registration | VARCHAR(40) | True | False |  | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:13 |
| legal_representative_user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/002_business_permissions_finance.sql:14 |
| submitted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:15 |
| approved_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:16 |
| approved_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:17 |
| rejection_reason | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:18 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:19 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:20 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:21 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:22 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:23 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:24 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/002_business_permissions_finance.sql:25 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/011_business_idempotency.sql:3 |
