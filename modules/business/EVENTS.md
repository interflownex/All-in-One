        # Events: Business

        Exchange: `all-in-one.domain`; routing keys:

        - `business.company.created`
- `business.company.submitted`
- `business.company.approved`
- `business.company.rejected`
- `business.user.invited`
- `business.role.assigned`
- `business.user.revoked`
- `valley.catalog.offer.synced`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
