from __future__ import annotations

from scripts.validate_repository_compat import (
    compatibility_exceptions,
    extract_errors,
    filter_validation_errors,
)


def test_validator_does_not_suppress_compatibility_conditions() -> None:
    conditions = compatibility_exceptions()

    assert conditions == {}


def test_filter_keeps_unknown_errors_blocking() -> None:
    known = "Falha anteriormente reconhecida."
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
