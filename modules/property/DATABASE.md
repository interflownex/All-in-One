        # Database: Property

        Schema relacional principal: `property`.

        ## Entidades planejadas

        - `property.properties`
- `property.units`
- `property.leases`
- `property.assemblies`
- `property.maintenance_orders`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
