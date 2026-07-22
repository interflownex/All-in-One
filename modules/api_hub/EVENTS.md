        # Events: API Hub

        Exchange: `all-in-one.domain`; routing keys:

        - `api.client.created`

- `api.client.submitted`
- `api.client.approved`
- `api.client.rejected`
- `api.key.created`
- `api.key.submitted`
- `api.key.approved`
- `api.key.rejected`
- `api.webhook.created`
- `api.webhook.submitted`
- `api.webhook.approved`
- `api.webhook.rejected`
- `api.integration_run.created`
- `api.integration_run.submitted`
- `api.integration_run.approved`
- `api.integration_run.rejected`
- `api.webhook.delivered`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
