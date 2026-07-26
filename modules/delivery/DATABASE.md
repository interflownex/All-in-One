        # Database: Delivery

        Schema relacional principal: `delivery`.

        ## Entidades planejadas

        - `delivery.delivery_requests`
- `delivery.quotes`
- `delivery.assignments`
- `delivery.proofs`
- `delivery.insurance_options`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
