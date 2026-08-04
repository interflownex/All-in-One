from __future__ import annotations

from pathlib import Path

import scripts.validate_repository_compat as validator


def test_validator_suppresses_only_replaced_cloudflare_rules() -> None:
    conditions = validator.compatibility_exceptions()

    assert conditions == validator.LEGACY_CLOUDFLARE_ERRORS
    assert len(conditions) == 5
    assert all(value is True for value in conditions.values())


def test_filter_keeps_unknown_errors_blocking() -> None:
    known = next(iter(validator.LEGACY_CLOUDFLARE_ERRORS))
    real_error = "Erro real que nao pode ser ocultado."

    remaining, suppressed = validator.filter_validation_errors(
        [known, real_error], validator.compatibility_exceptions()
    )

    assert suppressed == [known]
    assert remaining == [real_error]


def test_extract_errors_preserves_context() -> None:
    errors, context = validator.extract_errors(
        "Falhas de validacao encontradas:\n- Primeiro erro\ncontexto adicional\n"
    )

    assert errors == ["Primeiro erro"]
    assert context == ["contexto adicional"]


def test_cloudflare_contract_is_valid_in_repository() -> None:
    assert validator.validate_cloudflare_pages_contract() == []


def test_cloudflare_contract_fails_closed_for_missing_marker(
    tmp_path: Path, monkeypatch
) -> None:
    workflow = tmp_path / "cloudflare-pages.yml"
    workflow.write_text(
        "\n".join(
            marker
            for marker in validator.REQUIRED_CLOUDFLARE_MARKERS
            if marker != "uses: cloudflare/wrangler-action@v4"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "CLOUDFLARE_WORKFLOW", workflow)

    errors = validator.validate_cloudflare_pages_contract()

    assert errors == [
        "Contrato Cloudflare Pages endurecido deve conter: "
        "uses: cloudflare/wrangler-action@v4"
    ]


def test_cloudflare_contract_rejects_legacy_bypass(
    tmp_path: Path, monkeypatch
) -> None:
    workflow = tmp_path / "cloudflare-pages.yml"
    workflow.write_text(
        "\n".join(validator.REQUIRED_CLOUDFLARE_MARKERS)
        + "\ndeploy_enabled=false\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validator, "CLOUDFLARE_WORKFLOW", workflow)

    errors = validator.validate_cloudflare_pages_contract()

    assert errors == [
        "Contrato Cloudflare Pages não pode conter marcador legado: "
        "deploy_enabled=false"
    ]
