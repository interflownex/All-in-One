        # Events: Legal

        Exchange: `all-in-one.domain`; routing keys:

        - `legal.case.created`

- `legal.deadline.created`
- `legal.deadline.alerted`
- `legal.deadline.completed`
- `legal.hearing.scheduled`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
