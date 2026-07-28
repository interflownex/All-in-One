        # Database: AI Core

        Schema relacional principal: `ai_core`.

        ## Entidades planejadas

        - `ai_core.ai_memories`
- `ai_core.moderation_decisions`
- `ai_core.model_runs`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
