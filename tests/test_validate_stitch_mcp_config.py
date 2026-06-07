from __future__ import annotations

from pathlib import Path

from scripts.validate_stitch_mcp_config import validate_stitch_mcp_config


def write_config(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def valid_config(tmp_path: Path) -> Path:
    return write_config(
        tmp_path / "config.toml",
        """
[mcp_servers]
[mcp_servers.stitch]
url = 'https://stitch.googleapis.com/mcp'
http_headers = { Accept = 'application/json' }
env_http_headers = { 'X-Goog-Api-Key' = 'STITCH_API_KEY' }
""".lstrip(),
    )


def test_accepts_expected_env_header_config(tmp_path: Path) -> None:
    errors = validate_stitch_mcp_config(config_path=valid_config(tmp_path), root=Path.cwd())
    assert errors == []


def test_rejects_missing_stitch_server(tmp_path: Path) -> None:
    config = write_config(tmp_path / "config.toml", "[mcp_servers]\n")
    errors = validate_stitch_mcp_config(config_path=config, root=Path.cwd())
    assert any("[mcp_servers.stitch]" in error for error in errors)


def test_rejects_wrong_endpoint(tmp_path: Path) -> None:
    config = write_config(
        tmp_path / "config.toml",
        """
[mcp_servers]
[mcp_servers.stitch]
url = 'https://example.invalid/mcp'
http_headers = { Accept = 'application/json' }
env_http_headers = { 'X-Goog-Api-Key' = 'STITCH_API_KEY' }
""".lstrip(),
    )
    errors = validate_stitch_mcp_config(config_path=config, root=Path.cwd())
    assert any("https://stitch.googleapis.com/mcp" in error for error in errors)


def test_rejects_literal_api_key_header(tmp_path: Path) -> None:
    config = write_config(
        tmp_path / "config.toml",
        """
[mcp_servers]
[mcp_servers.stitch]
url = 'https://stitch.googleapis.com/mcp'
http_headers = { Accept = 'application/json', 'X-Goog-Api-Key' = 'AIzaSyLiteralKey' }
env_http_headers = { 'X-Goog-Api-Key' = 'STITCH_API_KEY' }
""".lstrip(),
    )
    errors = validate_stitch_mcp_config(config_path=config, root=Path.cwd())
    assert any("literal" in error for error in errors)


def test_requires_secret_when_active_policy_requests_remote_validation(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("STITCH_API_KEY", raising=False)
    errors = validate_stitch_mcp_config(config_path=valid_config(tmp_path), require_secret=True, root=Path.cwd())
    assert errors == ["Variavel obrigatoria ausente no ambiente: STITCH_API_KEY"]


def test_allows_repository_validation_without_personal_codex_config(tmp_path: Path) -> None:
    errors = validate_stitch_mcp_config(
        config_path=tmp_path / "missing-config.toml",
        require_codex_config=False,
        root=Path.cwd(),
    )
    assert errors == []
