        # Database: GED ECM

        Schema relacional principal: `document`.

        ## Entidades planejadas

        - `document.folders`
- `document.documents`
- `document.versions`
- `document.retention_policies`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
