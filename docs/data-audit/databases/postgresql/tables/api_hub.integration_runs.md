# `api_hub.integration_runs`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:25 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/010_api_hub_refinement.sql:26 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:27 |
| integration_type | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:28 |
| provider_name | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:29 |
| started_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:30 |
| ended_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:31 |
| log_summary | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:32 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:33 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:34 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:35 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:36 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:37 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:38 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/010_api_hub_refinement.sql:39 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/010_api_hub_refinement.sql:40 |
