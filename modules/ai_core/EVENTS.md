        # Events: AI Core

        Exchange: `all-in-one.domain`; routing keys:

        - `ai.memory.created`
- `ai.memory.indexed`
- `ai.memory.updated`
- `ai.moderation.created`
- `ai.moderation.completed`
- `ai.model_run.requested`
- `ai.model_run.completed`
- `ai.model_run.failed`
- `ai.model_run.cost_approved`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
