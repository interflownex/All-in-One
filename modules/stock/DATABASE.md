        # Database: Stock

        Schema relacional principal: `stock`.

        ## Entidades planejadas

        - `stock.suppliers`

- `stock.catalog_products`
- `stock.price_rules`
- `stock.supplier_orders`
- `stock.discount_quotes`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
