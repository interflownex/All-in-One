from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROVISIONER = ROOT / "scripts" / "mapbox" / "provision_valley_rider_tokens.mjs"
CONFIGURATOR = ROOT / "scripts" / "mapbox" / "configure_valley_rider_mapbox.sh"


def test_provisioner_requires_creator_and_public_scopes() -> None:
    content = PROVISIONER.read_text(encoding="utf-8")

    assert 'const PUBLIC_SCOPES = ["styles:read", "fonts:read"]' in content
    assert 'const REQUIRED_ADMIN_SCOPES = ["tokens:write", ...PUBLIC_SCOPES]' in content
    assert "Public scopes: styles:read, fonts:read" in content
    assert "Secret scopes: tokens:write" in content


def test_provisioner_explains_mapbox_scope_error() -> None:
    content = PROVISIONER.read_text(encoding="utf-8")

    assert "/scopes are invalid/i" in content
    assert "não possui todos os escopos exigidos" in content
    assert "Não reutilize o token anterior" in content
    assert "Todos os tokens criados nesta execução foram revogados" in content


def test_interactive_configurator_warns_before_reading_secret() -> None:
    content = CONFIGURATOR.read_text(encoding="utf-8")

    warning_position = content.index("O token temporário sk. precisa conter TODOS estes escopos")
    secret_prompt_position = content.index("Novo token temporário Mapbox (sk.)")

    assert warning_position < secret_prompt_position
    assert "Public scopes: styles:read, fonts:read" in content
    assert "Secret scopes: tokens:write" in content
    assert 'read -r -s -p "Novo token temporário Mapbox (sk.): "' in content
