        # Events: CRM

        Exchange: `all-in-one.domain`; routing keys:

        - `crm.lead.created`

- `crm.lead.qualified`
- `crm.lead.disqualified`
- `crm.opportunity.created`
- `crm.opportunity.proposed`
- `crm.opportunity.won`
- `crm.opportunity.lost`
- `crm.activity.created`
- `crm.activity.completed`
- `crm.campaign.created`
- `crm.campaign.launched`
- `crm.campaign.closed`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
