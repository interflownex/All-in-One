from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from modules.shared.delivery_postgres_store import DeliveryPostgresStore
from modules.shared.mobility_postgres_store import MobilityPostgresStore
from modules.shared.services_postgres_store import ServicesPostgresStore
from scripts.validate_postgres_real_dsn import REQUIRED_TABLES, REQUIRED_TRIGGERS
from scripts.verify_pg_indexes import REQUIRED_INDEXES
from tests.test_postgres_priority_stores_integration import EVENT_PREFIX_ALIASES, phone_from_nonce


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


def test_user_reference_columns_are_not_treated_as_business_entities() -> None:
    forbidden_entity_mappings = (
        'row.get("provider_user_id")) if row.get("provider_user_id")',
        'row.get("assigned_rider_user_id")) if row.get("assigned_rider_user_id")',
        'row.get("driver_user_id")) if row.get("driver_user_id")',
    )
    store_sources = [
        ROOT / "modules" / "shared" / "postgres_store.py",
        ROOT / "modules" / "shared" / "services_postgres_store.py",
        ROOT / "modules" / "shared" / "delivery_postgres_store.py",
        ROOT / "modules" / "shared" / "mobility_postgres_store.py",
    ]
    material = "\n".join(path.read_text(encoding="utf-8") for path in store_sources)

    assert not any(mapping in material for mapping in forbidden_entity_mappings)


def test_operational_user_references_do_not_become_audit_entity_ids() -> None:
    created_at = datetime.now(timezone.utc)
    common_row = {
        "id": "00000000-0000-0000-0000-000000000001",
        "user_id": "00000000-0000-0000-0000-000000000002",
        "status": "active",
        "metadata": {"runtime_payload": {}},
        "created_at": created_at,
        "updated_at": created_at,
        "created_by": "00000000-0000-0000-0000-000000000003",
        "updated_by": "00000000-0000-0000-0000-000000000003",
        "deleted_at": None,
        "idempotency_key": None,
    }

    services = ServicesPostgresStore.__new__(ServicesPostgresStore)
    delivery = DeliveryPostgresStore.__new__(DeliveryPostgresStore)
    mobility = MobilityPostgresStore.__new__(MobilityPostgresStore)

    assert services._resource("providers", {**common_row, "provider_user_id": common_row["user_id"]})["entity_id"] is None
    assert delivery._resource("delivery_requests", {**common_row, "assigned_rider_user_id": common_row["user_id"]})["entity_id"] is None
    assert mobility._resource("rides", {**common_row, "driver_user_id": common_row["user_id"]})["entity_id"] is None


def test_identity_priority_store_phone_does_not_collide_with_dsn_validator() -> None:
    assert phone_from_nonce("abcdef123456") != "+5511999999999"
