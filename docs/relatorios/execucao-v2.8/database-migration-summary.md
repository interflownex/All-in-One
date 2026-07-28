# Resumo de migrações PostgreSQL v2.8

**Arquivo com falha:** `database/postgres/migrations/029_unified_immutable_audit.sql`

**Código de saída:** `3`

```text
BEGIN
psql:database/postgres/migrations/029_unified_immutable_audit.sql:29: ERROR:  syntax error at or near "authorization"
LINE 19:     ADD COLUMN IF NOT EXISTS authorization TEXT,
                                      ^
```
