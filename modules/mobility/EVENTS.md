        # Events: Mobility

        Exchange: `all-in-one.domain`; routing keys:

        - `mobility.ride.requested`

- `mobility.ride.accepted`
- `mobility.ride.completed`
- `mobility.route.eta_quoted`
- `mobility.ticket.purchased`
- `mobility.ticket.used`
- `mobility.fare_rule.published`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
