        # Events: WMS

        Exchange: `all-in-one.domain`; routing keys:

        - `wms.warehouse.created`
- `wms.bin.created`
- `wms.inventory.received`
- `wms.inventory.allocated`
- `wms.picking.created`
- `wms.picking.completed`
- `wms.picking.closed`
- `wms.shipment.created`
- `wms.shipment.dispatched`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
