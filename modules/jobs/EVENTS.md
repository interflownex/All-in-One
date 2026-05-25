        # Events: Jobs

        Exchange: `all-in-one.domain`; routing keys:

        - `jobs.resume.created`
- `jobs.resume.ctps_imported`
- `jobs.employment.self_declared`
- `jobs.job_posting.created`
- `jobs.application.created`
- `jobs.resume.viewed`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
