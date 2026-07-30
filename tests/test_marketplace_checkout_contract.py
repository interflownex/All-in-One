from decimal import Decimal
from pathlib import Path

from modules.shared.marketplace_checkout_postgres_store import (
    MarketplaceCheckoutPostgresStore,
)

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "database"
    / "postgres"
    / "migrations"
    / "032_marketplace_checkout.sql"
)
ROLLBACK = (
    ROOT
    / "database"
    / "postgres"
    / "rollbacks"
    / "032_marketplace_checkout.sql"
)
STORE_FILES = [
    ROOT / "modules" / "shared" / name
    for name in (
        "marketplace_checkout_base.py",
        "marketplace_checkout_create.py",
        "marketplace_checkout_prepare.py",
        "marketplace_checkout_persist.py",
        "marketplace_checkout_payment.py",
        "marketplace_checkout_approve.py",
        "marketplace_checkout_release.py",
        "marketplace_checkout_expiration.py",
        "marketplace_checkout_postgres_store.py",
    )
]
ROUTES = ROOT / "modules" / "marketplace" / "checkout_routes.py"
BOOTSTRAP = ROOT / "modules" / "shared" / "__init__.py"
OPENAPI = ROOT / "modules" / "marketplace" / "OPENAPI.yaml"
CONTRACT = ROOT / "modules" / "marketplace" / "CHECKOUT_CONTRACT.md"


def test_migration_032_is_latest_and_models_immutable_checkout() -> None:
    migrations = sorted((ROOT / "database" / "postgres" / "migrations").glob("*.sql"))
    assert migrations[-1].name == MIGRATION.name
    sql = MIGRATION.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS marketplace.checkouts" in sql
    assert "CREATE TABLE IF NOT EXISTS marketplace.checkout_items" in sql
    assert "CREATE TABLE IF NOT EXISTS marketplace.checkout_operations" in sql
    assert "UNIQUE (user_id, idempotency_key)" in sql
    assert "UNIQUE (checkout_id, operation_type, idempotency_key)" in sql
    assert "REFERENCES stock.stock_reservations(id)" in sql
    assert "REFERENCES finance.wallets(id, user_id)" in sql
    assert "currency = 'BRL'" in sql
    assert "WHERE status IN ('stock_reserved', 'pending_payment')" in sql


def test_migration_has_explicit_manual_rollback_in_dependency_order() -> None:
    rollback = ROLLBACK.read_text(encoding="utf-8")
    operations = rollback.index("DROP TABLE IF EXISTS marketplace.checkout_operations")
    items = rollback.index("DROP TABLE IF EXISTS marketplace.checkout_items")
    checkouts = rollback.index("DROP TABLE IF EXISTS marketplace.checkouts")
    assert operations < items < checkouts
    assert "Executar somente em banco efêmero" in rollback


def test_checkout_hash_is_stable_for_equivalent_money() -> None:
    first = MarketplaceCheckoutPostgresStore.request_hash(
        cart_id="00000000-0000-0000-0000-000000000001",
        currency="BRL",
        expected_total_brl=Decimal("19.9"),
        wallet_id="00000000-0000-0000-0000-000000000002",
        payment_method="wallet",
    )
    replay = MarketplaceCheckoutPostgresStore.request_hash(
        cart_id="00000000-0000-0000-0000-000000000001",
        currency="BRL",
        expected_total_brl=Decimal("19.9000"),
        wallet_id="00000000-0000-0000-0000-000000000002",
        payment_method="wallet",
    )
    changed = MarketplaceCheckoutPostgresStore.request_hash(
        cart_id="00000000-0000-0000-0000-000000000001",
        currency="BRL",
        expected_total_brl=Decimal("20.00"),
        wallet_id="00000000-0000-0000-0000-000000000002",
        payment_method="wallet",
    )
    assert first == replay
    assert first != changed
    assert len(first) == 64


def test_routes_require_flag_idempotency_correlation_and_internal_scopes() -> None:
    routes = ROUTES.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    assert '"/valley/checkout"' in routes
    assert '"/valley/checkout/{checkout_id}"' in routes
    assert '"/valley/checkout/{checkout_id}/payment-result"' in routes
    assert '"/valley/checkout/expire"' in routes
    assert 'Header(..., alias="X-Idempotency-Key")' in routes
    assert routes.count('Header(..., alias="X-Correlation-Id")') >= 3
    assert "MARKETPLACE_CHECKOUT_V1_ENABLED" in routes
    assert "marketplace:checkout:payment" in routes
    assert "marketplace:checkout:expire" in routes
    assert 'module_name == "marketplace"' in bootstrap
    assert "register_checkout_routes(app)" in bootstrap


def test_store_uses_authoritative_stock_ledger_locks_audit_and_outbox() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in STORE_FILES)
    assert "marketplace.products.stock_quantity" not in source
    assert "FROM stock.inventory_items" in source
    assert source.count("FOR UPDATE") >= 8
    assert "FOR UPDATE SKIP LOCKED" in source
    assert "INSERT INTO finance.ledger_entries" in source
    assert "marketplace_purchase_authorized" in source
    assert "UPDATE finance.wallets" not in source
    assert "stock.reservation.created" in source
    assert "stock.reservation.committed" in source
    assert "stock.reservation.released" in source
    assert "stock.reservation.expired" in source
    assert "marketplace.checkout.started" in source
    assert "marketplace.checkout.confirmed" in source
    assert "finance.payment.authorized" in source
    assert "insert_postgres_audit" in source
    assert "INSERT INTO audit.domain_events" in source


def test_openapi_contract_keep_feature_off_and_exclude_later_phases() -> None:
    openapi = OPENAPI.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")
    combined = f"{openapi}\n{contract}"
    assert "version: 0.4.0" in openapi
    assert "/valley/checkout:" in openapi
    assert "/valley/checkout/{checkout_id}/payment-result:" in openapi
    assert "X-Idempotency-Key" in openapi
    assert "MARKETPLACE_CHECKOUT_V1_ENABLED=false" in contract
    assert "Delivery e Rider: fora deste incremento" in contract
    assert "Vision: inativo" in contract
    assert "delivery_requests" not in combined
    assert "rider_assignment" not in combined
    assert "vision.enabled" not in combined
