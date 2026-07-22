from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cloudflare_stream_tunnel_keeps_windows_service_persistent() -> None:
    script = (ROOT / "scripts" / "setup_cloudflare_stream_tunnel.ps1").read_text(
        encoding="utf-8"
    )

    assert "Set-Service -Name $service.Name -StartupType Automatic" in script
    assert "Start-Service -Name $service.Name" in script
    assert (
        "Tunnel Cloudflare configurado com persistencia no servico do Windows."
        in script
    )
    assert 'Write-Host "Tunnel id: $tunnelId"' in script


def test_docker_complete_pipeline_runs_git_auto_sync_after_push() -> None:
    script = (ROOT / "scripts" / "docker_complete_pipeline.ps1").read_text(
        encoding="utf-8"
    )

    assert "Etapa 5: Sincronizando com o repositorio Git" in script
    assert "scripts/git_auto_sync.ps1" in script
    assert "chore(docker): tag and push images to Docker Hub" in script


def test_stop_conflicting_valley_runtime_disables_communication_bridge() -> None:
    script = (ROOT / "scripts" / "stop_conflicting_valley_runtime.ps1").read_text(
        encoding="utf-8"
    )

    assert "'ValleyCommunicationBridge'" in script
    assert r"*\scripts\valley_communication_bridge.py*" in script
    assert "Runtime conflitante do VALLEY desligado de forma persistente." in script


def test_wsl_bootstrap_loads_environment_and_prepares_venv() -> None:
    script = (ROOT / "scripts" / "bootstrap_wsl_dev_environment.sh").read_text(
        encoding="utf-8"
    )

    assert "grep -qi microsoft /proc/version" in script
    assert 'source "$file"' in script
    assert 'python3 "$ROOT/scripts/configure_docker_dx.py"' in script
    assert 'load_env_file "$ROOT/.env.docker-dx"' in script
    assert (
        'export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-all-in-one-dx}"' in script
    )
    assert 'python -m pip install -r "$ROOT/requirements-dev.txt"' in script
