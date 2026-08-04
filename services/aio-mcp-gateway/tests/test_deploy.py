from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_ROOT = SERVICE_ROOT / "deploy"


def _load(name: str, filename: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, DEPLOY_ROOT / filename)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render = _load("aio_mcp_render", "render_cloud_run.py")
rollback = _load("aio_mcp_rollback", "rollback_cloud_run.py")

IMAGE = "us-docker.pkg.dev/sample-project/aio/aio-mcp-gateway@sha256:" + "a" * 64
SERVICE_ACCOUNT = "aio-mcp-runtime@sample-project.iam.gserviceaccount.com"


def test_manifest_requires_immutable_digest() -> None:
    with pytest.raises(render.DeployConfigurationError, match="imutável"):
        render.validate_image_digest(
            "us-docker.pkg.dev/sample-project/aio/aio-mcp-gateway:latest"
        )


def test_manifest_renders_without_unresolved_tokens() -> None:
    revision = render.revision_name(IMAGE, "release-1")
    manifest = render.render_manifest(
        image_digest=IMAGE,
        service_account=SERVICE_ACCOUNT,
        revision=revision,
    )
    assert IMAGE in manifest
    assert SERVICE_ACCOUNT in manifest
    assert revision in manifest
    assert "${" not in manifest
    assert "https://mcp.brasildesconto.com.br" in manifest
    assert "aio-mcp-redis-url" in manifest


def test_revision_defaults_to_digest_prefix() -> None:
    assert render.revision_name(IMAGE, None) == "aio-mcp-gateway-" + "a" * 12


def test_deploy_command_is_scoped_to_project_and_region(tmp_path: Path) -> None:
    manifest = tmp_path / "service.yaml"
    command = render.gcloud_command(
        manifest=manifest,
        project="sample-project",
        region="southamerica-east1",
    )
    assert command[:4] == ["gcloud", "run", "services", "replace"]
    assert command[-5:] == [
        "--project",
        "sample-project",
        "--region",
        "southamerica-east1",
        "--quiet",
    ]


def test_rollback_only_accepts_gateway_revision() -> None:
    with pytest.raises(
        rollback.RollbackConfigurationError,
        match="aio-mcp-gateway",
    ):
        rollback.validate_revision("other-service-00001")


def test_rollback_command_routes_all_traffic() -> None:
    command = rollback.rollback_command(
        revision="aio-mcp-gateway-release-1",
        project="sample-project",
        region="southamerica-east1",
    )
    assert command[:5] == [
        "gcloud",
        "run",
        "services",
        "update-traffic",
        "aio-mcp-gateway",
    ]
    assert "aio-mcp-gateway-release-1=100" in command
    assert command[-1] == "--quiet"
