from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_operations_runbook_covers_backup_restore_and_disaster_recovery() -> None:
    operations = (ROOT / "docs" / "OPERATIONS.md").read_text(encoding="utf-8")
    deployment = (ROOT / "docs" / "DEPLOYMENT.md").read_text(encoding="utf-8")

    assert "## Backup, Restore E DR" in operations
    assert "pg_dump" in operations
    assert "pg_restore" in operations
    assert "mongodump" in operations
    assert "mongorestore" in operations
    assert "rpo_minutes" in operations
    assert "rto_minutes" in operations
    assert "drill de restore" in operations.casefold()
    assert "health" in operations
    assert "## Producao" in deployment
    assert "backup/restore validado" in deployment.casefold()
    assert "disaster recovery" in deployment.casefold()
    assert "rpo/rto" in deployment.casefold()
