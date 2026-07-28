        # Events: Riders

        Exchange: `all-in-one.domain`; routing keys:

        - `rider.submitted`
- `rider.approved`
- `rider.rejected`
- `rider.vehicle.approved`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
