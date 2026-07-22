        # Events: Identity

        Exchange: `all-in-one.domain`; routing keys:

        - `identity.user.created`

- `identity.user.verified`
- `identity.user.duplicate_detected`
- `identity.document.created`
- `identity.document.approved`
- `identity.document.rejected`
- `identity.biometric.captured`
- `identity.session.created`
- `identity.session.revoked`
- `identity.kyc.submitted`
- `identity.kyc.approved`
- `identity.kyc.rejected`
- `identity.consent.recorded`

        Eventos carregam `event_id`, `occurred_at`, `actor_user_id`, `user_id`,
        `entity_id`, `correlation_id`, `schema_version` e payload minimizado.
        Consumidores devem ser idempotentes.
