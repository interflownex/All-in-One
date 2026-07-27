        # Database: Business

        Schema relacional principal: `business`.

        ## Entidades planejadas

        - `business.companies`
- `business.branches`
- `business.company_documents`
- `business.user_company_memberships`
- `business.catalog_offers`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
