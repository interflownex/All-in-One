# `document.documents`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:102 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:103 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:104 |
| storage_key | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:105 |
| filename | VARCHAR(255) | False | False |  | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:106 |
| mime_type | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:107 |
| version_number | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:108 |
| retention_until | DATE | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:109 |
| searchable_text | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:110 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:111 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:112 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:113 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:114 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:115 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:116 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:117 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:42 |
