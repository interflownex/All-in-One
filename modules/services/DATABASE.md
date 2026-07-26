        # Database: One Services

        Schema relacional principal: `services`.

        ## Entidades planejadas

        - `services.providers`
- `services.visits`
- `services.quotes`
- `services.service_contracts`
- `services.evidence`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
