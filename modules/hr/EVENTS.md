        # Events: HR HCM ATS LMS

        Exchange: `all-in-one.domain`; routing keys:

        - `hr.employee.created`
- `hr.payroll.opened`
- `hr.payroll.closed`
- `hr.training.assigned`
- `hr.training.completed`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
