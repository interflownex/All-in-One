        # Events: One Services

        Exchange: `all-in-one.domain`; routing keys:

        - `services.visit.created`
- `services.visit.completed`
- `services.quote.created`
- `services.contract.created`
- `services.contract.completed`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
