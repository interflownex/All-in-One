        # Database: Marketplace

        Schema relacional principal: `marketplace`.

        ## Entidades planejadas

        - `marketplace.stores`
- `marketplace.products`
- `marketplace.carts`
- `marketplace.orders`
- `marketplace.reviews`
- `marketplace.disputes`
- `marketplace.pepita_grants`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
