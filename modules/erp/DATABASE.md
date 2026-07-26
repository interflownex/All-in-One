        # Database: ERP

        Schema relacional principal: `erp`.

        ## Entidades planejadas

        - `erp.accounts`
- `erp.payables`
- `erp.receivables`
- `erp.cost_centers`
- `erp.fiscal_documents`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
