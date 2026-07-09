from __future__ import annotations

import re
from pathlib import Path

from scripts.validate_postgres_real_dsn import REQUIRED_TABLES, REQUIRED_TRIGGERS
from scripts.verify_pg_indexes import REQUIRED_INDEXES
from tests.test_postgres_priority_stores_integration import EVENT_PREFIX_ALIASES


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "database" / "postgres" / "migrations"


def _migration_sql() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(MIGRATIONS_DIR.glob("*.sql")))


def test_postgres_contract_required_tables_exist_in_migrations() -> None:
    sql = _migration_sql()
    missing = []
    for table_name in sorted(REQUIRED_TABLES):
        schema, table = table_name.split(".")
        pattern = rf"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+{re.escape(schema)}\.{re.escape(table)}\b"
        if not re.search(pattern, sql, re.IGNORECASE):
            missing.append(table_name)

    assert missing == []


def test_postgres_contract_required_triggers_exist_in_migrations() -> None:
    sql = _migration_sql()
    missing = [
        trigger_name
        for trigger_name in sorted(REQUIRED_TRIGGERS)
        if not re.search(rf"CREATE\s+TRIGGER\s+{re.escape(trigger_name)}\b", sql, re.IGNORECASE)
    ]

    assert missing == []


def test_postgres_contract_required_indexes_exist_in_migrations() -> None:
    sql = _migration_sql()
    missing = [
        index_name
        for index_name in sorted(REQUIRED_INDEXES)
        if not re.search(
            rf"CREATE\s+(?:UNIQUE\s+)?INDEX\s+IF\s+NOT\s+EXISTS\s+{re.escape(index_name)}\b",
            sql,
            re.IGNORECASE,
        )
    ]

    assert missing == []


def test_postgres_priority_store_event_prefix_aliases_are_documented() -> None:
    assert EVENT_PREFIX_ALIASES["riders"] == ("rider.%", "riders.%")
