#!/usr/bin/env python3
"""Valida a política visual e de entrega reutilizável de todos os aplicativos."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "ui" / "global_visual_delivery_policy.json"
SKIP_PARTS = {
    ".git",
    ".next",
    ".dart_tool",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "vendor",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_projects(root: Path, policy: dict[str, Any]) -> list[str]:
    scope = policy.get("scope", {})
    roots = scope.get("application_roots", [])
    markers = scope.get("project_markers", [])
    projects: set[str] = set()

    for root_name in roots:
        base = root / root_name
        if not base.exists():
            continue
        for marker in markers:
            for path in base.rglob(marker):
                if any(part in SKIP_PARTS for part in path.parts):
                    continue
                projects.add(path.parent.relative_to(root).as_posix())

    return sorted(projects)


def collect_local_opt_outs(root: Path, policy: dict[str, Any]) -> list[str]:
    opt_outs: list[str] = []
    for root_name in policy.get("scope", {}).get("application_roots", []):
        base = root / root_name
        if not base.exists():
            continue
        for path in base.rglob("visual-delivery.override.json"):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            try:
                override = load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                opt_outs.append(f"{path.relative_to(root)}: override inválido: {exc}")
                continue
            if override.get("enabled") is False or override.get("mandatory") is False:
                opt_outs.append(f"{path.relative_to(root)}: tentativa de desativar a política global")
    return opt_outs


def validate_policy(root: Path, policy: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    if policy.get("mandatory") is not True:
        violations.append("A política deve permanecer com mandatory=true.")
    if policy.get("local_opt_out_allowed") is not False:
        violations.append("A política deve permanecer com local_opt_out_allowed=false.")

    sources = policy.get("sources_of_truth", {})
    required_sources = (
        "brand_assets",
        "brand_identity",
        "official_assets_root",
        "delivery_standard",
    )
    for key in required_sources:
        value = sources.get(key)
        if not value:
            violations.append(f"Fonte de verdade ausente: {key}")
            continue
        if not (root / value).exists():
            violations.append(f"Fonte de verdade não encontrada: {value}")

    typography = policy.get("typography", {})
    mobile = typography.get("mobile_sp", {})
    minimums = {
        "small_auxiliary": 16,
        "body": 18,
        "form_input": 18,
        "form_label": 18,
        "section_subtitle": 20,
        "button": 22,
        "screen_title": 32,
        "hero_title_min": 36,
        "hero_title_max": 40,
    }
    for token, minimum in minimums.items():
        value = mobile.get(token)
        if not isinstance(value, (int, float)) or value < minimum:
            violations.append(
                f"Token tipográfico mobile_sp.{token} deve ser numérico e >= {minimum}."
            )

    rules = typography.get("rules", {})
    if rules.get("equal_font_size_for_equivalent_buttons") is not True:
        violations.append("Botões equivalentes devem manter o mesmo tamanho de fonte.")
    if rules.get("reduce_single_button_font_to_fit") is not False:
        violations.append("É proibido reduzir apenas a fonte de um botão para fazê-lo caber.")
    if rules.get("respect_system_font_scaling") is not True:
        violations.append("A escala de fonte do sistema deve ser respeitada.")

    brand = policy.get("brand_governance", {})
    if brand.get("official_logo_immutable") is not True:
        violations.append("A logomarca oficial deve permanecer imutável.")

    buttons = policy.get("buttons", {})
    required_button_flags = {
        "intent_buttons_use_images": False,
        "intent_buttons_use_icons": False,
        "high_relief": True,
        "visible_soft_shadow": True,
        "upper_highlight": True,
        "debossed_text": True,
        "base_without_text_required": True,
        "transparent_png_required_when_exported": True,
    }
    for key, expected in required_button_flags.items():
        if buttons.get(key) is not expected:
            violations.append(f"Regra obrigatória de botão inválida: {key}={expected!r}.")

    reusable = policy.get("reusable_assets", {})
    if reusable.get("required") is not True:
        violations.append("Ativos reutilizáveis devem ser obrigatórios.")
    if reusable.get("screen_crops_are_reusable_assets") is not False:
        violations.append("Recortes de tela não podem ser classificados como ativos reutilizáveis.")
    if reusable.get("transparent_png_when_applicable") is not True:
        violations.append("PNG transparente deve ser exigido quando aplicável.")

    package = policy.get("delivery_package", {})
    if package.get("required") is not True:
        violations.append("O pacote ZIP deve ser obrigatório.")
    required_contents = {
        "tela pronta",
        "elementos PNG reutilizáveis",
        "arquivo Markdown",
        "MANIFESTO_SHA256.json",
    }
    if not required_contents.issubset(set(package.get("ordered_contents", []))):
        violations.append("O ZIP não declara todos os conteúdos obrigatórios.")
    required_downloads = {
        "ZIP completo",
        "imagem da tela pronta",
        "arquivo Markdown",
        "manifesto JSON",
    }
    if not required_downloads.issubset(set(package.get("required_chat_downloads", []))):
        violations.append("A entrega no chat não declara todos os links obrigatórios.")

    manifest = policy.get("manifest", {})
    if manifest.get("filename") != "MANIFESTO_SHA256.json":
        violations.append("O manifesto deve se chamar MANIFESTO_SHA256.json.")
    if not {"arquivo", "sha256", "bytes", "mime_type"}.issubset(
        set(manifest.get("required_fields", []))
    ):
        violations.append("Campos mínimos do manifesto JSON estão incompletos.")

    approved = policy.get("approved_screens", {})
    if approved.get("modify_only_with_explicit_owner_authorization") is not True:
        violations.append("Telas aprovadas só podem mudar com autorização expressa.")

    enforcement = policy.get("enforcement", {})
    for key in ("validator", "workflow", "tests"):
        value = enforcement.get(key)
        if not value or not (root / value).is_file():
            violations.append(f"Componente de enforcement ausente: {key} -> {value}")
    if enforcement.get("failure_blocks_merge") is not True:
        violations.append("Falhas no contrato visual devem bloquear merge.")

    violations.extend(collect_local_opt_outs(root, policy))

    projects = discover_projects(root, policy)
    if not projects:
        violations.append("Nenhum aplicativo foi descoberto nos diretórios de escopo.")

    return sorted(set(violations))


def main() -> int:
    if not POLICY_PATH.is_file():
        print(f"Política global não encontrada: {POLICY_PATH.relative_to(ROOT)}")
        return 1

    try:
        policy = load_json(POLICY_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Falha ao carregar a política global: {exc}")
        return 1

    violations = validate_policy(ROOT, policy)
    projects = discover_projects(ROOT, policy)

    if violations:
        print("Falha no padrão visual global:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Padrão visual global aprovado.")
    print(f"Aplicativos/projetos cobertos automaticamente: {len(projects)}")
    for project in projects:
        print(f"- {project}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
