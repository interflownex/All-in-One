        # Events: Delivery

        Exchange: `all-in-one.domain`; routing keys:

        - `delivery.request.created`

- `delivery.rider.assigned`
- `delivery.picked_up`
- `delivery.completed`
- `delivery.proof.recorded`
- `delivery.cancelled`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
