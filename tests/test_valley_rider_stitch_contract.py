from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "valley_rider" / "src" / "App.tsx"
MAP = ROOT / "apps" / "valley_rider" / "src" / "MapboxRouteMap.tsx"
PLATFORM = ROOT / "apps" / "valley_rider" / "src" / "riderPlatform.ts"
CSS = ROOT / "apps" / "valley_rider" / "src" / "index.css"
README = ROOT / "apps" / "valley_rider" / "README.md"


def test_valley_rider_uses_official_stitch_functional_groups() -> None:
    source = APP.read_text(encoding="utf-8")
    for contract in (
        "Cadastro e validação",
        "Disponibilidade, mapa e localização",
        "Ofertas e corridas",
        "Registrar prova",
        "Ganhos, wallet e repasses",
        "Chat e ocorrências",
        "Histórico",
        "Avaliações",
    ):
        assert contract in source


def test_mapbox_gps_route_and_eta_are_real_contracts() -> None:
    app = APP.read_text(encoding="utf-8")
    map_source = MAP.read_text(encoding="utf-8")
    platform = PLATFORM.read_text(encoding="utf-8")
    assert "navigator.geolocation.watchPosition" in app
    assert "/directions/v5/mapbox/driving-traffic/" in platform
    assert "geometries=geojson" in platform
    assert "distance_km" in app and "eta_minutes" in app
    assert "mapbox-gl-js/v3.25.0" in map_source
    assert "mapbox://styles/mapbox/navigation-night-v1" in map_source
    assert "map-placeholder" not in app


def test_all_sensitive_workflows_bind_to_existing_api_hub_resources() -> None:
    source = APP.read_text(encoding="utf-8")
    for endpoint in (
        "/registrations",
        "/auth/login",
        "/identity/kyc/submit",
        "/riders/resources/rider_profiles",
        "/riders/resources/rider_documents",
        "/riders/resources/vehicles",
        "/delivery/resources/delivery_requests",
        "/delivery/resources/proofs",
        "/mobility/resources/rides",
        "/finance/resources/wallets",
        "/finance/resources/ledger_entries",
        "/finance/resources/splits",
        "/marketplace/resources/disputes",
    ):
        assert endpoint in source


def test_no_invalid_negative_ledger_or_forbidden_brand_asset() -> None:
    source = APP.read_text(encoding="utf-8")
    assert "amount_brl: (-amount)" not in source
    assert "valley-logo-transparent.svg" not in source
    assert "valley-logo-official.png" in source
    assert "valley-riders-logo" not in source


def test_no_decorative_placeholder_and_accessible_touch_contract() -> None:
    source = APP.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    assert "map-placeholder" not in source
    assert "onClick={() => {}}" not in source
    assert "min-height:48px" in css.replace(" ", "")
    assert 'font-family:"Manrope"' in css.replace(" ", "")
    assert "Jornadas funcionais" in readme
