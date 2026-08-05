#!/usr/bin/env bash
set -euo pipefail

: "${PGHOST:=localhost}"
: "${PGPORT:=5432}"
: "${PGDATABASE:=all_in_one}"
: "${PGUSER:=all_in_one}"

psql_cmd=(psql -X -v ON_ERROR_STOP=1 -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE")

"${psql_cmd[@]}" <<'SQL'
DROP ROLE IF EXISTS compliance_rls_probe;
CREATE ROLE compliance_rls_probe NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
GRANT USAGE ON SCHEMA compliance TO compliance_rls_probe;
GRANT SELECT ON compliance.catalog_versions, compliance.field_registry TO compliance_rls_probe;
SQL

owner_catalog_count=$("${psql_cmd[@]}" -qAtc "SELECT COUNT(*) FROM compliance.catalog_versions;")
owner_field_count=$("${psql_cmd[@]}" -qAtc "SELECT COUNT(*) FROM compliance.field_registry;")

test "$owner_catalog_count" -gt 0
test "$owner_field_count" -gt 0

flags=$("${psql_cmd[@]}" -qAtc "SELECT string_agg(relname || ':' || relrowsecurity || ':' || relforcerowsecurity, ',' ORDER BY relname) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'compliance' AND relname IN ('catalog_versions', 'field_registry');")
test "$flags" = "catalog_versions:true:true,field_registry:true:true"

probe_catalog_count=$("${psql_cmd[@]}" -qAtc "SET ROLE compliance_rls_probe; SELECT COUNT(*) FROM compliance.catalog_versions;")
probe_field_count=$("${psql_cmd[@]}" -qAtc "SET ROLE compliance_rls_probe; SELECT COUNT(*) FROM compliance.field_registry;")

test "$probe_catalog_count" = "0"
test "$probe_field_count" = "0"

"${psql_cmd[@]}" -f database/postgres/rollbacks/036_compliance_rls_deny_all_baseline.sql

rollback_flags=$("${psql_cmd[@]}" -qAtc "SELECT string_agg(relname || ':' || relrowsecurity || ':' || relforcerowsecurity, ',' ORDER BY relname) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'compliance' AND relname IN ('catalog_versions', 'field_registry');")
test "$rollback_flags" = "catalog_versions:false:false,field_registry:false:false"

rollback_catalog_count=$("${psql_cmd[@]}" -qAtc "SET ROLE compliance_rls_probe; SELECT COUNT(*) FROM compliance.catalog_versions;")
rollback_field_count=$("${psql_cmd[@]}" -qAtc "SET ROLE compliance_rls_probe; SELECT COUNT(*) FROM compliance.field_registry;")

test "$rollback_catalog_count" = "$owner_catalog_count"
test "$rollback_field_count" = "$owner_field_count"

"${psql_cmd[@]}" -f database/postgres/migrations/036_compliance_rls_deny_all_baseline.sql

reapply_catalog_count=$("${psql_cmd[@]}" -qAtc "SET ROLE compliance_rls_probe; SELECT COUNT(*) FROM compliance.catalog_versions;")
reapply_field_count=$("${psql_cmd[@]}" -qAtc "SET ROLE compliance_rls_probe; SELECT COUNT(*) FROM compliance.field_registry;")

test "$reapply_catalog_count" = "0"
test "$reapply_field_count" = "0"

"${psql_cmd[@]}" <<'SQL'
REVOKE SELECT ON compliance.catalog_versions, compliance.field_registry FROM compliance_rls_probe;
REVOKE USAGE ON SCHEMA compliance FROM compliance_rls_probe;
DROP ROLE compliance_rls_probe;
SQL
