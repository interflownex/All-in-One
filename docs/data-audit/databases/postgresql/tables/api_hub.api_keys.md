# `api_hub.api_keys`

| Campo           | Tipo         | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                  |
| --------------- | ------------ | ----- | ----- | ---------------------- | -------------------------------- | ---------------------------------------------------------- |
| id              | UUID         | False | True  |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:4  |
| user_id         | UUID         | False | False | identity.users.id      | pseudônimo vinculável            | database/postgres/migrations/010_api_hub_refinement.sql:5  |
| company_id      | UUID         | True  | False | business.companies.id  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:6  |
| client_id       | UUID         | True  | False | api_hub.api_clients.id | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:7  |
| key_name        | VARCHAR(150) | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:8  |
| key_hash        | TEXT         | False | False |                        | restrito                         | database/postgres/migrations/010_api_hub_refinement.sql:9  |
| key_hint        | VARCHAR(20)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:10 |
| scopes          | JSONB        | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:11 |
| expires_at      | TIMESTAMPTZ  | True  | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:12 |
| last_used_at    | TIMESTAMPTZ  | True  | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:13 |
| status          | VARCHAR(40)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:14 |
| idempotency_key | VARCHAR(120) | True  | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:15 |
| metadata        | JSONB        | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:16 |
| created_at      | TIMESTAMPTZ  | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:17 |
| updated_at      | TIMESTAMPTZ  | False | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:18 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                        | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:19 |
| created_by      | UUID         | True  | False | identity.users.id      | pseudônimo vinculável            | database/postgres/migrations/010_api_hub_refinement.sql:20 |
| updated_by      | UUID         | True  | False | identity.users.id      | pseudônimo vinculável            | database/postgres/migrations/010_api_hub_refinement.sql:21 |
