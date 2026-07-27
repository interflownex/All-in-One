        # Database: WMS

        Schema relacional principal: `wms`.

        ## Entidades planejadas

        - `wms.warehouses`
- `wms.bins`
- `wms.inventory`
- `wms.picking_waves`
- `wms.shipments`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
