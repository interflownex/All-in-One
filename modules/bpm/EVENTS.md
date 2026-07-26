        # Events: BPM

        Exchange: `all-in-one.domain`; routing keys:

        - `bpm.process.started`

- `bpm.task.created`
- `bpm.task.escalated`
- `bpm.task.completed`
- `bpm.sla_policy.published`

        Eventos carregam event_id, occurred_at, actor_user_id, user_id,
        entity_id, correlation_id, schema_version e payload minimizado.
        Consumidores devem ser idempotentes.
