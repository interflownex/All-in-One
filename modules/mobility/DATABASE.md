        # Database: Mobility

        Schema relacional principal: `mobility`.

        ## Entidades planejadas

        - `mobility.rides`
- `mobility.routes`
- `mobility.stops`
- `mobility.tickets`
- `mobility.fare_rules`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
