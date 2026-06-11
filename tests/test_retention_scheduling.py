from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docker_compose_schedules_retention_worker_in_safe_dry_run_mode() -> None:
    compose = (ROOT / "infra" / "docker" / "docker-compose.yml").read_text(encoding="utf-8")

    assert "retention-worker:" in compose
    assert "workers/retention_worker/Dockerfile" in compose
    assert "ALL_IN_ONE_RETENTION_POSTGRES_DSN" in compose
    assert "ALL_IN_ONE_RETENTION_POLL_SECONDS" in compose
    assert "retention_review_daily --dry-run" in compose
    assert "anonymization_worker_hourly --dry-run" in compose
    assert "deletion_worker_daily --dry-run" in compose
    assert "legal_hold_reconciliation_daily" in compose


def test_kubernetes_declares_retention_cronjob_with_secret_dsn() -> None:
    base = ROOT / "infra" / "kubernetes" / "base"
    manifest = "\n".join(path.read_text(encoding="utf-8") for path in sorted(base.glob("*.yaml")))

    assert "kind: CronJob" in manifest
    assert "name: retention-worker" in manifest
    assert 'schedule: "0 * * * *"' in manifest
    assert "concurrencyPolicy: Forbid" in manifest
    assert "ALL_IN_ONE_RETENTION_POSTGRES_DSN: REPLACE_WITH_VAULT_REFERENCE" in manifest
    assert 'args: ["--postgres", "--job", "retention_review_daily", "--dry-run"]' in manifest
