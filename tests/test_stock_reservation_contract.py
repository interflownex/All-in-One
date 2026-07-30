from decimal import Decimal
from pathlib import Path

from modules.shared.stock_postgres_store import StockPostgresStore

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database" / "postgres" / "migrations" / "027_stock_inventory_reservations.sql"
ROLLBACK = ROOT / "database" / "postgres" / "rollbacks" / "027_stock_inventory_reservations.sql"
STORE = ROOT / "modules" / "shared" / "stock_postgres_store.py"
MAIN = ROOT / "modules" / "stock" / "main.py"
OPENAPI = ROOT / "modules" / "stock" / "OPENAPI.yaml"


def test_migration_027_is_latest_and_defines_authoritative_balances() -> None:
    migrations = sorted((ROOT / "database" / "postgres" / "migrations").glob("*.sql"))
    assert migrations[-1].name == MIGRATION.name

    sql = MIGRATION.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS stock.inventory_items" in sql
    assert "CREATE TABLE IF NOT EXISTS stock.stock_reservations" in sql
    assert "GENERATED ALWAYS AS (physical_quantity - reserved_quantity) STORED" in sql
    assert "reserved_quantity <= physical_quantity" in sql
    assert "UNIQUE (user_id, company_id, idempotency_key)" in sql
    assert "WHERE status = 'reserved'" in sql
    assert "REFERENCES marketplace.products(id)" in sql


def test_migration_has_explicit_manual_rollback_in_dependency_order() -> None:
    rollback = ROLLBACK.read_text(encoding="utf-8")
    reservations = rollback.index("DROP TABLE IF EXISTS stock.stock_reservations")
    inventory = rollback.index("DROP TABLE IF EXISTS stock.inventory_items")
    assert reservations < inventory
    assert "Executar somente em banco efêmero" in rollback


def test_store_uses_row_locks_skip_locked_and_atomic_outbox() -> None:
    source = STORE.read_text(encoding="utf-8")
    assert source.count("FOR UPDATE") >= 7
    assert "FOR UPDATE SKIP LOCKED" in source
    assert "stock.reservation.created" in source
    assert "stock.reservation.rejected" in source
    assert "stock.reservation.committed" in source
    assert "stock.reservation.released" in source
    assert "stock.reservation.expired" in source
    assert "INSERT INTO audit.domain_events" in source
    assert "idempotency_conflict" in source


def test_request_hash_is_stable_for_equivalent_decimal_bodies() -> None:
    first = StockPostgresStore.reservation_request_hash(
        inventory_item_id="00000000-0000-0000-0000-000000000001",
        order_id="00000000-0000-0000-0000-000000000002",
        quantity=Decimal("2"),
        expires_in_seconds=900,
    )
    repeated = StockPostgresStore.reservation_request_hash(
        inventory_item_id="00000000-0000-0000-0000-000000000001",
        order_id="00000000-0000-0000-0000-000000000002",
        quantity=Decimal("2.0000"),
        expires_in_seconds=900,
    )
    different = StockPostgresStore.reservation_request_hash(
        inventory_item_id="00000000-0000-0000-0000-000000000001",
        order_id="00000000-0000-0000-0000-000000000002",
        quantity=Decimal("3"),
        expires_in_seconds=900,
    )
    assert first == repeated
    assert first != different
    assert len(first) == 64


def test_api_requires_authentication_idempotency_and_correlation() -> None:
    main = MAIN.read_text(encoding="utf-8")
    assert 'app = create_module_app("stock", version="0.3.0")' in main
    assert 'Header(..., alias="X-Idempotency-Key")' in main
    assert main.count('Header(..., alias="X-Correlation-Id")') >= 5
    assert "actor: Actor = Depends(actor_from_headers)" in main
    assert "MARKETPLACE_CHECKOUT_V1_ENABLED" not in main


def test_openapi_exposes_only_stock_foundation_not_checkout_or_delivery() -> None:
    contract = OPENAPI.read_text(encoding="utf-8")
    assert "version: 0.3.0" in contract
    assert "  /inventory/items:" in contract
    assert "  /reservations:" in contract
    assert "  /reservations/{reservation_id}/commit:" in contract
    assert "  /reservations/{reservation_id}/release:" in contract
    assert "  /reservations/expire:" in contract
    assert "/checkout" not in contract
    assert "delivery" not in contract.casefold()
    assert "vision" not in contract.casefold()
