from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "database"
    / "postgres"
    / "migrations"
    / "033_marketplace_checkout_mercado_pago.sql"
)
ROLLBACK = (
    ROOT
    / "database"
    / "postgres"
    / "rollbacks"
    / "032_marketplace_checkout_attempts.sql"
)
STORE = ROOT / "modules" / "shared" / "marketplace_checkout_postgres_store.py"
ROUTES = ROOT / "modules" / "shared" / "marketplace_checkout_routes.py"
SHARED_INIT = ROOT / "modules" / "shared" / "__init__.py"
OPENAPI = ROOT / "modules" / "marketplace" / "checkout" / "OPENAPI.yaml"
CONTRACT = ROOT / "modules" / "marketplace" / "CHECKOUT_CONTRACT.md"


def test_migration_033_is_latest_and_extends_checkout_payment_methods() -> None:
    migrations = sorted((ROOT / "database" / "postgres" / "migrations").glob("*.sql"))
    assert migrations[-1].name == MIGRATION.name

    sql = MIGRATION.read_text(encoding="utf-8")
    assert (
        "DROP CONSTRAINT IF EXISTS marketplace_checkout_payment_method_allowed" in sql
    )
    assert "payment_method IN ('wallet', 'mercado_pago')" in sql


def test_rollback_032_is_explicit_and_dependency_safe() -> None:
    rollback = ROLLBACK.read_text(encoding="utf-8")
    table = rollback.index("DROP TABLE IF EXISTS marketplace.checkout_attempts")
    function = rollback.index(
        "DROP FUNCTION IF EXISTS marketplace.protect_checkout_attempt()"
    )
    assert table < function
    assert "Executar somente em banco efêmero" in rollback


def test_store_orchestrates_checkout_stock_wallet_ledger_and_compensation() -> None:
    source = STORE.read_text(encoding="utf-8")
    assert source.count("FOR UPDATE") >= 8
    assert "marketplace.checkout_attempts" in source
    assert "stock.inventory_items" in source
    assert "stock.stock_reservations" in source
    assert "finance.wallets" in source
    assert "finance.escrows" in source
    assert "finance.ledger_entries" in source
    assert "escrow_hold" in source
    assert "payment_failed" in source
    assert "payment_status = 'authorized'" in source
    assert 'settled": False' in source
    assert "marketplace.checkout.started" in source
    assert "marketplace.order.created" in source
    assert "finance.payment.authorized" in source
    assert "finance.payment.failed" in source
    assert "stock.reservation.created" in source
    assert "stock.reservation.committed" in source
    assert "stock.reservation.released" in source
    assert "marketplace.checkout.confirmed" in source
    assert "marketplace.checkout.cancelled" in source
    assert "marketplace.products.stock_quantity" not in source
    assert "Delivery" not in source
    assert "Rider" not in source


def test_routes_are_registered_only_for_marketplace_and_flag_new_checkouts() -> None:
    routes = ROUTES.read_text(encoding="utf-8")
    shared_init = SHARED_INIT.read_text(encoding="utf-8")

    assert 'os.getenv("MARKETPLACE_CHECKOUT_V1_ENABLED", "false")' in routes
    assert 'os.getenv("ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN")' in routes
    assert '@app.post("/valley/checkout", status_code=201)' in routes
    assert '@app.get("/valley/checkout/{checkout_id}")' in routes
    assert '@app.post("/valley/checkout/{checkout_id}/confirm")' in routes
    assert '@app.post("/valley/checkout/{checkout_id}/cancel")' in routes
    assert routes.count('alias="X-Idempotency-Key"') == 2
    assert routes.count('alias="X-Correlation-Id"') == 5
    assert "Checkout desativado por feature flag" in routes
    assert 'if module_name == "marketplace"' in shared_init
    assert "register_marketplace_checkout_routes(app)" in shared_init


def test_checkout_openapi_and_contract_preserve_scope() -> None:
    openapi = OPENAPI.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "version: 0.1.0" in openapi
    assert "  /valley/checkout:" in openapi
    assert "  /valley/checkout/{checkout_id}:" in openapi
    assert "  /valley/checkout/{checkout_id}/confirm:" in openapi
    assert "  /valley/checkout/{checkout_id}/cancel:" in openapi
    assert "MARKETPLACE_CHECKOUT_V1_ENABLED" in openapi
    assert "escrow" in openapi.casefold()
    assert "settled" in openapi.casefold() or "liquidado" in openapi.casefold()
    assert "  /delivery" not in openapi.casefold()
    assert "  /rider" not in openapi.casefold()

    assert "**Versão:** 0.2.0" in contract
    assert "032_marketplace_checkout_attempts.sql" in contract
    assert "feature flag" in contract.casefold()
    assert "não liquida o valor ao lojista" in contract.casefold()
    assert "Vision permanece inativo" in contract
