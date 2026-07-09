import os
import sys
import psycopg

POSTGRES_DSN = os.getenv("ALL_IN_ONE_POSTGRES_MATRIX_DSN")

REQUIRED_INDEXES = [
    "idx_outbox_dispatcher_ready",
    "idx_audit_events_correlation",
    "idx_finance_ledger_wallet_lookup",
    "idx_finance_gold_ledger_entity_lookup",
    "idx_jobs_resumes_visibility",
    "idx_business_membership_lookup",
]

def verify_indexes():
    if not POSTGRES_DSN:
        print("Erro: ALL_IN_ONE_POSTGRES_MATRIX_DSN nao configurada.")
        return 1

    try:
        with psycopg.connect(POSTGRES_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT indexname FROM pg_indexes WHERE indexname = ANY(%s)", (REQUIRED_INDEXES,))
                found = {row[0] for row in cur.fetchall()}

                missing = set(REQUIRED_INDEXES) - found
                if missing:
                    print(f"Falha: Indices ausentes no banco: {', '.join(missing)}")
                    return 1

                print(f"Sucesso: Todos os {len(REQUIRED_INDEXES)} indices de performance foram localizados no banco.")
                return 0
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(verify_indexes())
