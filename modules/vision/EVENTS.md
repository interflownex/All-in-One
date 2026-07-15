        # Events: Vision

        Exchange: `all-in-one.domain`; routing keys:

        - `vision.device.registered`
- `vision.stream.started`
- `vision.recording.stored`
- `vision.motion.detected`
- `vision.incident.created`
- `vision.incident.resolved`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
