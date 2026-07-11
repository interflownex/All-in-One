from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cloudflare_stream_tunnel_keeps_windows_service_persistent() -> None:
    script = (ROOT / "scripts" / "setup_cloudflare_stream_tunnel.ps1").read_text(encoding="utf-8")

    assert "Set-Service -Name $service.Name -StartupType Automatic" in script
    assert "Start-Service -Name $service.Name" in script
    assert "Tunnel Cloudflare configurado com persistencia no servico do Windows." in script
    assert "Write-Host \"Tunnel id: $tunnelId\"" in script


def test_docker_complete_pipeline_runs_git_auto_sync_after_push() -> None:
    script = (ROOT / "scripts" / "docker_complete_pipeline.ps1").read_text(encoding="utf-8")

    assert "Etapa 5: Sincronizando com o repositorio Git" in script
    assert "scripts/git_auto_sync.ps1" in script
    assert "chore(docker): tag and push images to Docker Hub" in script
