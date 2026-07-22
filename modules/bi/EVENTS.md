        # Events: BI

        Exchange: `all-in-one.domain`; routing keys:

        - `bi.dataset.created`

- `bi.dataset.refreshed`
- `bi.dataset.published`
- `bi.dashboard.created`
- `bi.dashboard.published`
- `bi.dashboard.archived`
- `bi.indicator.created`
- `bi.indicator.submitted`
- `bi.indicator.cancelled`
- `bi.indicator.completed`
- `bi.export.requested`
- `bi.export.completed`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
