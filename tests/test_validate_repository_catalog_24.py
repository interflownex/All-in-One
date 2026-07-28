from __future__ import annotations

from scripts import validate_repository_catalog_24


def _catalog(size: int) -> dict[str, list[dict[str, str]]]:
    return {"modules": [{"slug": f"module-{index}"} for index in range(size)]}


def test_catalog_compatibility_ignores_only_obsolete_count(monkeypatch, capsys) -> None:
    target = validate_repository_catalog_24.validate_repository
    monkeypatch.setattr(target, "CATALOG", _catalog(24))

    def fake_main() -> int:
        errors: list[str] = []
        target.fail("Esperados 25 modulos; catalogo possui 24.", errors)
        target.fail("Falha real preservada.", errors)
        print("Repositorio validado com sucesso! Todos os 25 modulos e infraestrutura estao em conformidade.")
        return 1 if errors else 0

    monkeypatch.setattr(target, "main", fake_main)

    assert validate_repository_catalog_24.main() == 1
    output = capsys.readouterr().out
    assert "Todos os 24 modulos ativos" in output


def test_catalog_compatibility_rejects_unexpected_module_count(monkeypatch, capsys) -> None:
    target = validate_repository_catalog_24.validate_repository
    monkeypatch.setattr(target, "CATALOG", _catalog(23))

    called = False

    def fake_main() -> int:
        nonlocal called
        called = True
        return 0

    monkeypatch.setattr(target, "main", fake_main)

    assert validate_repository_catalog_24.main() == 1
    assert called is False
    assert "esperados 24 módulos ativos" in capsys.readouterr().err
