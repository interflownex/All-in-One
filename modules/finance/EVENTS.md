        # Events: Finance Pay Billing Fiscal

        Exchange: `all-in-one.domain`; routing keys:

        - `payment.escrow.created`

- `payment.escrow.released`
- `payment.refunded`
- `payment.split.executed`
- `valley.gold.ledger.posted`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
