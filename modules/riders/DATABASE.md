        # Database: Riders

        Schema relacional principal: `delivery`.

        ## Entidades planejadas

        - `delivery.rider_profiles`
- `delivery.rider_documents`
- `delivery.vehicles`
- `delivery.rider_reviews`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
