        # Database: Health

        Schema relacional principal: `health`.

        ## Entidades planejadas

        - `health.patients`
- `health.appointments`
- `health.medical_records`
- `health.prescriptions`
- `health.beds`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
