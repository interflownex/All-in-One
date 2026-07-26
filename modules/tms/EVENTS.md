        # Events: TMS

        Exchange: `all-in-one.domain`; routing keys:

        - `tms.carrier.created`
- `tms.carrier.submitted`
- `tms.carrier.approved`
- `tms.carrier.rejected`
- `tms.route.created`
- `tms.route.activated`
- `tms.freight.created`
- `tms.freight.approved`
- `tms.freight.dispatched`
- `tms.freight.completed`
- `tms.delivery.proved`
- `tms.freight.audit_created`
- `tms.freight.audit_closed`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
