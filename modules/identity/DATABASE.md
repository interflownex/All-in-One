        # Database: Identity

        Schema relacional principal: `identity`.

        ## Entidades planejadas

        - `identity.users`
- `identity.documents`
- `identity.biometrics`
- `identity.sessions`
- `identity.identity_verifications`
- `identity.consent_records`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
