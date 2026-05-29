BEGIN;

ALTER TABLE identity.users ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.documents ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.biometrics ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.mfa_devices ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.sessions ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.identity_verifications ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.consent_records ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;
ALTER TABLE identity.duplicate_attempts ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100) UNIQUE;

CREATE INDEX IF NOT EXISTS idx_identity_users_idempotency ON identity.users(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_identity_documents_idempotency ON identity.documents(idempotency_key) WHERE idempotency_key IS NOT NULL;

COMMIT;
