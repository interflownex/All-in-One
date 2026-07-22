        # Database: Vision

        Schema relacional principal: `vision`.

        ## Entidades planejadas

        - `vision.devices`

- `vision.streams`
- `vision.recordings`
- `vision.motion_alerts`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
