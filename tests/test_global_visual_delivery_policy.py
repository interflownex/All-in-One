from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.validate_global_visual_delivery import discover_projects, validate_policy


def make_policy() -> dict:
    return {
        "mandatory": True,
        "local_opt_out_allowed": False,
        "scope": {
            "application_roots": ["apps", "desktop", "frontend", "mobile", "web"],
            "project_markers": ["package.json", "pubspec.yaml", "*.csproj"],
        },
        "sources_of_truth": {
            "brand_assets": "config/branding/authorized_assets.json",
            "brand_identity": "config/branding/brand_identity.json",
            "official_assets_root": "assets/brand",
            "delivery_standard": "docs/design/PADRAO_GLOBAL_ENTREGA_VISUAL_REUTILIZAVEL.md",
        },
        "design_governance": {
            "design_is_strategic_project_requirement": True,
            "required_in_all_applications": True,
            "design_review_required_before_merge": True,
            "required_quality_dimensions": [
                "clareza da jornada",
                "consistência visual",
                "legibilidade",
                "acessibilidade",
                "responsividade",
                "hierarquia da informação",
                "feedback de interação",
                "redução de esforço do usuário",
                "continuidade entre telas",
            ],
            "required_artifacts_before_implementation": [
                "fluxo da jornada",
                "tela de referência ou wireframe",
                "inventário de componentes reutilizáveis",
                "estados vazio, carregando, erro e sucesso",
                "critérios de aceite de design e experiência",
            ],
            "review_gates": {
                "ux_review_required": True,
                "accessibility_review_required": True,
                "responsive_review_required": True,
                "visual_consistency_review_required": True,
                "visual_regression_review_required": True,
            },
            "minimum_viewports": ["mobile_small", "mobile_standard", "tablet"],
            "definition_of_done": [
                "interface consistente com a identidade e o design system",
                "estados interativos e mensagens definidos",
                "sem overflow ou corte de conteúdo",
                "texto legível com escala do sistema",
                "navegação sem duplicação desnecessária",
            ],
            "prohibited": ["tratar design como acabamento opcional"],
        },
        "typography": {
            "mobile_sp": {
                "small_auxiliary": 16,
                "body": 18,
                "form_input": 18,
                "form_label": 18,
                "section_subtitle": 20,
                "button": 22,
                "screen_title": 32,
                "hero_title_min": 36,
                "hero_title_max": 40,
            },
            "rules": {
                "equal_font_size_for_equivalent_buttons": True,
                "reduce_single_button_font_to_fit": False,
                "respect_system_font_scaling": True,
            },
        },
        "brand_governance": {"official_logo_immutable": True},
        "buttons": {
            "intent_buttons_use_images": False,
            "intent_buttons_use_icons": False,
            "high_relief": True,
            "visible_soft_shadow": True,
            "upper_highlight": True,
            "debossed_text": True,
            "base_without_text_required": True,
            "transparent_png_required_when_exported": True,
        },
        "reusable_assets": {
            "required": True,
            "screen_crops_are_reusable_assets": False,
            "transparent_png_when_applicable": True,
        },
        "delivery_package": {
            "required": True,
            "ordered_contents": [
                "tela pronta",
                "elementos PNG reutilizáveis",
                "arquivo Markdown",
                "MANIFESTO_SHA256.json",
            ],
            "required_chat_downloads": [
                "ZIP completo",
                "imagem da tela pronta",
                "arquivo Markdown",
                "manifesto JSON",
            ],
        },
        "manifest": {
            "filename": "MANIFESTO_SHA256.json",
            "required_fields": ["arquivo", "sha256", "bytes", "mime_type"],
        },
        "approved_screens": {
            "modify_only_with_explicit_owner_authorization": True,
        },
        "enforcement": {
            "validator": "scripts/validate_global_visual_delivery.py",
            "workflow": ".github/workflows/global-visual-delivery.yml",
            "tests": "tests/test_global_visual_delivery_policy.py",
            "failure_blocks_merge": True,
        },
    }


def materialize_required_files(root: Path) -> None:
    for relative in (
        "config/branding/authorized_assets.json",
        "config/branding/brand_identity.json",
        "docs/design/PADRAO_GLOBAL_ENTREGA_VISUAL_REUTILIZAVEL.md",
        "scripts/validate_global_visual_delivery.py",
        ".github/workflows/global-visual-delivery.yml",
        "tests/test_global_visual_delivery_policy.py",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    (root / "assets/brand").mkdir(parents=True, exist_ok=True)
    app = root / "apps/valley"
    app.mkdir(parents=True, exist_ok=True)
    (app / "package.json").write_text("{}", encoding="utf-8")


def test_valid_policy_covers_discovered_apps(tmp_path: Path) -> None:
    materialize_required_files(tmp_path)
    policy = make_policy()

    assert discover_projects(tmp_path, policy) == ["apps/valley"]
    assert validate_policy(tmp_path, policy) == []


def test_rejects_local_opt_out(tmp_path: Path) -> None:
    materialize_required_files(tmp_path)
    override = tmp_path / "apps/valley/visual-delivery.override.json"
    override.write_text(json.dumps({"enabled": False}), encoding="utf-8")

    violations = validate_policy(tmp_path, make_policy())

    assert any("tentativa de desativar" in violation for violation in violations)


@pytest.mark.parametrize(
    ("path", "value", "expected"),
    [
        (("mandatory",), False, "mandatory=true"),
        (("local_opt_out_allowed",), True, "local_opt_out_allowed=false"),
        (("design_governance", "design_is_strategic_project_requirement"), False, "design_is_strategic_project_requirement"),
        (("design_governance", "review_gates", "accessibility_review_required"), False, "accessibility_review_required"),
        (("typography", "mobile_sp", "button"), 18, "mobile_sp.button"),
        (("buttons", "debossed_text"), False, "debossed_text"),
        (("reusable_assets", "screen_crops_are_reusable_assets"), True, "Recortes de tela"),
    ],
)
def test_rejects_contract_regressions(
    tmp_path: Path,
    path: tuple[str, ...],
    value: object,
    expected: str,
) -> None:
    materialize_required_files(tmp_path)
    policy = make_policy()
    target = policy
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value

    violations = validate_policy(tmp_path, policy)

    assert any(expected in violation for violation in violations)


def test_rejects_missing_design_artifacts(tmp_path: Path) -> None:
    materialize_required_files(tmp_path)
    policy = make_policy()
    policy["design_governance"]["required_artifacts_before_implementation"] = []

    violations = validate_policy(tmp_path, policy)

    assert any("Artefatos obrigatórios de design" in violation for violation in violations)
