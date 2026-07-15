        # Events: Jobs

        Exchange: `all-in-one.domain`; routing keys:

        - `jobs.resume.created`
- `jobs.resume.ctps_imported`
- `jobs.employment.self_declared`
- `jobs.resume_document.created`
- `jobs.job_posting.created`
- `jobs.job_posting.published`
- `jobs.job_posting.closed`
- `jobs.application.created`
- `jobs.application.reviewed`
- `jobs.application.shortlisted`
- `jobs.application.interview_scheduled`
- `jobs.application.rejected`
- `jobs.application.withdrawn`
- `jobs.resume.viewed`
- `jobs.resume_access_log.created`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
