        # Database: TMS

        Schema relacional principal: `tms`.

        ## Entidades planejadas

        - `tms.carriers`
- `tms.freights`
- `tms.routes`
- `tms.proofs_of_delivery`
- `tms.freight_audits`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
