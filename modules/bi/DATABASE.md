        # Database: BI

        Schema relacional principal: `bi`.

        ## Entidades planejadas

        - `bi.datasets`
- `bi.dashboards`
- `bi.indicators`
- `bi.exports`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
