        # Database: API Hub

        Schema relacional principal: `api_hub`.

        ## Entidades planejadas

        - `api_hub.api_clients`
- `api_hub.api_keys`
- `api_hub.webhooks`
- `api_hub.integration_runs`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
