        # Events: Business

        Exchange: `all-in-one.domain`; routing keys:

        - `business.company.created`

- `business.company.submitted`
- `business.company.approved`
- `business.company.rejected`
- `business.branche.created`
- `business.branche.submitted`
- `business.branche.cancelled`
- `business.branche.completed`
- `business.company_document.created`
- `business.company_document.submitted`
- `business.company_document.cancelled`
- `business.company_document.completed`
- `business.user.invited`
- `business.role.assigned`
- `business.user.revoked`
- `business.catalog_offer.created`
- `business.catalog_offer.submitted`
- `business.catalog_offer.cancelled`
- `business.catalog_offer.completed`
- `valley.catalog.offer.synced`
- `business.catalog_offer.paused`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
