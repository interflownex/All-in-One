        # Events: Marketplace

        Exchange: `all-in-one.domain`; routing keys:

        - `marketplace.store.created`

- `marketplace.product.created`
- `marketplace.order.created`
- `marketplace.order.paid`
- `marketplace.order.delivered`
- `marketplace.dispute.created`
- `support.ticket.created`
- `support.ticket.triaged`
- `support.ticket.resolved`
- `support.ticket.closed`
- `valley.review.created`
- `valley.review.published`
- `valley.review.rejected`
- `valley.pepitas.granted`

        Eventos carregam event_id, occurred_at, actor_user_id, user_id,
        entity_id, correlation_id, schema_version e payload minimizado.
        Consumidores devem ser idempotentes.
