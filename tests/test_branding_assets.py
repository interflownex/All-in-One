import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "config" / "branding" / "brand_identity.json"
MANIFEST = ROOT / "config" / "branding" / "authorized_assets.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_versioned_official_brand_assets_are_declared_and_are_png() -> None:
    identity = load_json(IDENTITY)
    manifest = load_json(MANIFEST)

    expected = {
        "all_in_one": identity["platform_brand"]["logo_asset"],
        "valley": identity["valley_brand"]["logo_asset"],
    }

    for brand_id, asset in expected.items():
        assert manifest["brands"][brand_id]["canonical_repository_asset"] == asset
        path = ROOT / asset
        assert path.is_file()
        assert path.suffix.lower() == ".png"
        assert path.read_bytes().startswith(PNG_SIGNATURE)
        assert "versionado" in manifest["brands"][brand_id]["status"]


def test_reconstructed_logos_are_explicitly_forbidden() -> None:
    manifest = load_json(MANIFEST)
    forbidden = {
        asset
        for brand in manifest["brands"].values()
        for asset in brand.get("legacy_or_reconstructed_assets_forbidden", [])
    }
    assert "assets/brand/all-in-one-logo-transparent.svg" in forbidden
    assert "assets/brand/valley-logo-transparent.svg" in forbidden


def test_riders_requires_original_binary_and_forbids_substitution() -> None:
    identity = load_json(IDENTITY)
    manifest = load_json(MANIFEST)
    riders = manifest["brands"]["valley_riders"]

    assert identity["riders_brand"]["logo_asset"] == riders["canonical_repository_asset"]
    assert riders["original_filename"] == "LOGO OFICIAL VALLEY RIDERS_2.png"
    assert "pendente" in riders["status"]
    assert riders["substitution_allowed"] is False


def test_brand_policy_requires_explicit_authorization_and_immediate_remediation() -> None:
    manifest = load_json(MANIFEST)
    policy = manifest["policy"]

    assert policy["explicit_authorization_required_for_change"] is True
    assert policy["transparent_background_required"] is True
    assert policy["autonomous_remediation"]["enabled"] is True
    assert set(policy["authorized_operations"]) == {
        "remover_apenas_o_fundo_externo_sem_tocar_na_marca",
        "redimensionar_proporcionalmente",
    }


def test_app_brand_scopes_are_separated() -> None:
    identity = load_json(IDENTITY)
    assert set(identity["valley_apps"]) == {"valley", "valley-business"}
    assert set(identity["riders_apps"]) == {"valley-rider", "all-in-one-riders"}
