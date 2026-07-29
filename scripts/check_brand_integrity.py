#!/usr/bin/env python3
"""Valida e restaura referências canônicas das marcas oficiais do grupo."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY_PATH = ROOT / "config" / "branding" / "brand_identity.json"
MANIFEST_PATH = ROOT / "config" / "branding" / "authorized_assets.json"

TEXT_SUFFIXES = {".tsx", ".ts", ".jsx", ".js", ".html", ".css", ".scss", ".md"}
SKIP_PARTS = {"node_modules", "dist", "build", ".git", "coverage", ".next"}
SCAN_ROOTS = ("apps", "desktop", "frontend")

KNOWN_ALIASES = {
    "assets/brand/all-in-one-logo-transparent.svg": "assets/brand/all-in-one-logo-official.png",
    "assets/brand/all-in-one-logo-light-official.png": "assets/brand/all-in-one-logo-official.png",
    "assets/brand/valley-logo-transparent.svg": "assets/brand/valley-logo-official.png",
}

PROHIBITED_STYLE = re.compile(
    r"(?:filter|transform|rotate|clip-path|mask|mix-blend-mode|opacity|"
    r"border-radius|object-fit\s*:\s*cover|background-image)\s*:",
    re.IGNORECASE,
)

HTML_REFERENCE = re.compile(r"(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
MARKDOWN_REFERENCE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
BRAND_PATH = re.compile(r"assets/brand/[^\s\"'`)>,;]+", re.IGNORECASE)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_asset(value: str) -> str:
    return value.strip().split("?", 1)[0].split("#", 1)[0].lstrip("/")


def frontend_files() -> list[Path]:
    files: list[Path] = []
    for root_name in SCAN_ROOTS:
        base = ROOT / root_name
        if not base.exists():
            continue
        files.extend(
            path
            for path in base.rglob("*")
            if path.is_file()
            and path.suffix.lower() in TEXT_SUFFIXES
            and not any(part in SKIP_PARTS for part in path.parts)
            and "src/main/assets" not in path.as_posix()
        )
    readme = ROOT / "README.md"
    if readme.exists():
        files.append(readme)
    return sorted(set(files))


def allowed_assets(identity: dict) -> set[str]:
    allowed: set[str] = set()
    for key in ("platform_brand", "valley_brand", "riders_brand"):
        brand = identity.get(key, {})
        logo = brand.get("logo_asset")
        if logo:
            allowed.add(normalized_asset(logo))
        for favicon in brand.get("favicon_assets", {}).values():
            allowed.add(normalized_asset(favicon))
    return allowed


def pending_assets(manifest: dict) -> set[str]:
    pending: set[str] = set()
    for brand in manifest.get("brands", {}).values():
        status = str(brand.get("status", ""))
        asset = brand.get("canonical_repository_asset")
        if asset and "pendente" in status:
            pending.add(normalized_asset(asset))
    return pending


def replace_known_aliases(text: str) -> tuple[str, int]:
    changes = 0
    for alias, canonical in KNOWN_ALIASES.items():
        for source, target in ((alias, canonical), (f"/{alias}", f"/{canonical}")):
            count = text.count(source)
            if count:
                text = text.replace(source, target)
                changes += count
    return text, changes


def references_in(text: str) -> set[str]:
    references = {match.group(1) for match in HTML_REFERENCE.finditer(text)}
    references.update(match.group(1) for match in MARKDOWN_REFERENCE.finditer(text))
    references.update(match.group(0) for match in BRAND_PATH.finditer(text))
    return {normalized_asset(value) for value in references if "assets/brand/" in value}


def style_fragments(path: Path, text: str) -> list[tuple[int, str]]:
    """Retorna unidades sintáticas pequenas para evitar falsos positivos minificados."""
    if path.suffix.lower() not in {".css", ".scss"}:
        return list(enumerate(text.splitlines(), start=1))

    fragments: list[tuple[int, str]] = []
    offset = 0
    for block in text.split("}"):
        line = text.count("\n", 0, offset) + 1
        fragments.append((line, block))
        offset += len(block) + 1
    return fragments


def fragment_targets_brand_art(fragment: str) -> bool:
    selector = fragment.split("{", 1)[0].lower()
    return bool(
        re.search(r"(?:logo|brand[-_]{1,2}(?:logo|mark|image|img))", selector)
        or ("brand" in selector and re.search(r"\bimg\b", selector))
    )


def validate_manifest(identity: dict, manifest: dict) -> list[str]:
    violations: list[str] = []
    if not manifest.get("policy", {}).get("explicit_authorization_required_for_change"):
        violations.append("Manifesto deve exigir autorização explícita para alterar a arte.")
    if not manifest.get("policy", {}).get("autonomous_remediation", {}).get("enabled"):
        violations.append("Manifesto deve habilitar remediação imediata de violações claras.")

    manifest_assets = {
        normalized_asset(brand["canonical_repository_asset"]): brand
        for brand in manifest.get("brands", {}).values()
        if brand.get("canonical_repository_asset")
    }
    for asset in allowed_assets(identity):
        if "favicon" in asset:
            continue
        if asset not in manifest_assets:
            violations.append(f"Ativo canônico ausente do manifesto: {asset}")

    for asset, brand in manifest_assets.items():
        status = str(brand.get("status", ""))
        path = ROOT / asset
        if "versionado" in status and not path.is_file():
            violations.append(f"Ativo oficial declarado como versionado não existe: {asset}")
    return violations


def scan(fix: bool) -> tuple[list[str], list[str]]:
    identity = load_json(IDENTITY_PATH)
    manifest = load_json(MANIFEST_PATH)
    allowed = allowed_assets(identity)
    pending = pending_assets(manifest)
    violations = validate_manifest(identity, manifest)
    changed_files: list[str] = []

    for path in frontend_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(ROOT)

        if fix:
            repaired, count = replace_known_aliases(text)
            if count:
                path.write_text(repaired, encoding="utf-8")
                text = repaired
                changed_files.append(str(relative))

        for alias in KNOWN_ALIASES:
            if alias in text or f"/{alias}" in text:
                violations.append(f"{relative}: referência legada ou reconstruída: {alias}")

        for reference in references_in(text):
            if reference in pending:
                violations.append(
                    f"{relative}: ativo oficial ainda pendente foi referenciado; não use substituto: {reference}"
                )
            elif reference not in allowed:
                violations.append(f"{relative}: ativo de marca não autorizado: {reference}")

        for line_number, fragment in style_fragments(path, text):
            if not fragment_targets_brand_art(fragment):
                continue
            match = PROHIBITED_STYLE.search(fragment)
            if match:
                violations.append(
                    f"{relative}:{line_number}: transformação visual proibida próxima à marca: {match.group(0)}"
                )

    brand_component = ROOT / "apps" / "all-in-one-business" / "src" / "components" / "BrandLogo.tsx"
    if not brand_component.exists():
        violations.append("Componente BrandLogo.tsx obrigatório não encontrado.")

    return sorted(set(violations)), changed_files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Substitui aliases conhecidos pelos ativos canônicos antes da validação.",
    )
    args = parser.parse_args()

    violations, changed_files = scan(fix=args.fix)

    if changed_files:
        print("Referências de marca restauradas automaticamente:")
        for path in changed_files:
            print(f"- {path}")

    if violations:
        print("Falha na integridade das marcas oficiais:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print("Integridade das marcas aprovada: ativos canônicos e regras de uso preservados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
