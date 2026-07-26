        # Database: CRM

        Schema relacional principal: `crm`.

        ## Entidades planejadas

        - `crm.leads`
- `crm.opportunities`
- `crm.activities`
- `crm.campaigns`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
