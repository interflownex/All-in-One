        # Database: Legal

        Schema relacional principal: `legal`.

        ## Entidades planejadas

        - `legal.cases`
- `legal.deadlines`
- `legal.hearings`
- `legal.legal_contracts`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
