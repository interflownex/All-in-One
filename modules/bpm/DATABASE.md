        # Database: BPM

        Schema relacional principal: `bpm`.

        ## Entidades planejadas

        - `bpm.processes`
- `bpm.workflow_instances`
- `bpm.tasks`
- `bpm.sla_policies`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
