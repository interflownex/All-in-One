#!/usr/bin/env python3
"""Falha a validação quando o front-end viola a integridade da marca oficial."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_ASSET = "/assets/brand/all-in-one-logo-light-official.png"
FRONTEND_SUFFIXES = {".tsx", ".ts", ".jsx", ".js", ".html", ".css", ".scss"}
SKIP_PARTS = {"node_modules", "dist", "build", ".git", "coverage"}

# A marca só pode ser redimensionada proporcionalmente. Estas propriedades
# alteram desenho, cor, orientação, recorte ou composição visual.
PROHIBITED_NEAR_LOGO = re.compile(
    r"(?:filter|transform|rotate|clip-path|mask|mix-blend-mode|opacity|"
    r"border-radius|object-fit\s*:\s*cover|background-image)\s*:",
    re.IGNORECASE,
)
DIRECT_LOGO_REFERENCE = re.compile(r"(?:logo|brand)[^\n]{0,180}", re.IGNORECASE)
IMG_SOURCE = re.compile(
    r"(?:src|href)\s*=\s*[\"']([^\"']*(?:logo|brand)[^\"']*)[\"']", re.IGNORECASE
)


def frontend_files() -> list[Path]:
    apps = ROOT / "apps"
    return sorted(
        path
        for path in apps.rglob("*")
        if path.is_file()
        and path.suffix.lower() in FRONTEND_SUFFIXES
        and not any(part in SKIP_PARTS for part in path.parts)
    )


def main() -> int:
    violations: list[str] = []
    official_usage = 0

    for path in frontend_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(ROOT)

        official_usage += text.count(OFFICIAL_ASSET)

        for match in IMG_SOURCE.finditer(text):
            source = match.group(1)
            if "all-in-one" in source.lower() and source != OFFICIAL_ASSET:
                violations.append(
                    f"{relative}: referência de marca não oficial: {source}"
                )

        for match in DIRECT_LOGO_REFERENCE.finditer(text):
            fragment = match.group(0)
            if PROHIBITED_NEAR_LOGO.search(fragment):
                violations.append(
                    f"{relative}: estilo proibido próximo de referência à logomarca: "
                    f"{fragment.strip()[:160]}"
                )

    brand_component = ROOT / "apps/all-in-one-business/src/components/BrandLogo.tsx"
    if not brand_component.exists():
        violations.append("Componente BrandLogo.tsx obrigatório não encontrado.")

    if official_usage == 0:
        violations.append(
            f"Nenhum uso do asset oficial foi encontrado: {OFFICIAL_ASSET}"
        )

    if violations:
        print("Falha na integridade da marca oficial:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print(
        "Integridade da marca aprovada: "
        f"{official_usage} referência(s) ao asset oficial; nenhuma transformação proibida."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
