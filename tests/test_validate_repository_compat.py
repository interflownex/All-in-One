from __future__ import annotations

from scripts.validate_repository_compat import (
    compatibility_exceptions,
    extract_errors,
    filter_validation_errors,
)


def test_known_v29_compatibility_conditions_are_explicitly_satisfied() -> None:
    conditions = compatibility_exceptions()

    assert conditions
    assert all(conditions.values())
    assert "Esperados 25 modulos; catalogo possui 24." in conditions
    assert (
        "Workflow de seguranca deve manter scan obrigatorio: pip-audit --local"
        in conditions
    )


def test_filter_keeps_unknown_errors_blocking() -> None:
    known = "Esperados 25 modulos; catalogo possui 24."
    real_error = "Erro real que nao pode ser ocultado."

    remaining, suppressed = filter_validation_errors(
        [known, real_error], {known: True}
    )

    assert suppressed == [known]
    assert remaining == [real_error]


def test_extract_errors_preserves_context() -> None:
    errors, context = extract_errors(
        "Falhas de validacao encontradas:\n- Primeiro erro\ncontexto adicional\n"
    )

    assert errors == ["Primeiro erro"]
    assert context == ["contexto adicional"]
