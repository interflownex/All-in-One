        # Events: ERP

        Exchange: `all-in-one.domain`; routing keys:

        - `erp.account.created`

- `erp.cost_center.created`
- `erp.payable.created`
- `erp.payment.approved`
- `erp.payable.paid`
- `erp.receivable.created`
- `erp.receivable.received`
- `erp.receivable.reconciled`
- `erp.invoice.created`
- `erp.invoice.submitted`
- `erp.invoice.completed`
- `erp.invoice.cancelled`

        Eventos carregam event_id, occurred_at, actor_user_id, user_id,
        entity_id, correlation_id, schema_version e payload minimizado.
        Consumidores devem ser idempotentes.
