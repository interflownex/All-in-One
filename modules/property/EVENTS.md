        # Events: Property

        Exchange: `all-in-one.domain`; routing keys:

        - `property.lease.created`

- `property.lease.activated`
- `property.lease.terminated`
- `property.maintenance.requested`
- `property.maintenance.scheduled`
- `property.maintenance.completed`

        Eventos carregam event_id, occurred_at, actor_user_id, user_id,
        entity_id, correlation_id, schema_version e payload minimizado.
        Consumidores devem ser idempotentes.
