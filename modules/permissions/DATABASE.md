        # Database: Permissions

        Schema relacional principal: `permissions`.

        ## Entidades planejadas

        - `permissions.roles`
- `permissions.permissions`
- `permissions.user_roles`
- `permissions.access_policies`
- `permissions.approval_limits`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
