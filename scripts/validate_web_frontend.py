#!/usr/bin/env python3
"""Valida cobertura da Home, rotas Stitch e ausencia de controles obviamente mortos."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "all-in-one"


def main() -> int:
    manifest = json.loads((ROOT / "config/stitch/screen_manifest.json").read_text())
    sync = json.loads((ROOT / "config/stitch/sync_state.json").read_text())
    app_source = (APP / "src/App.tsx").read_text()
    home_source = (APP / "src/pages/Home.tsx").read_text()
    smart_crud = (APP / "src/components/SmartCRUD.tsx").read_text()

    projects = sync.get("projects", {})
    screen_count = sum(len(project.get("screens", {})) for project in projects.values())
    assert len(projects) == manifest["project_count"] == 25, "Cobertura Stitch deve conter 25 projetos."
    assert screen_count == manifest["screen_count"] == 180, "Cobertura Stitch deve conter 180 telas."

    missing_ids = [
        f"{module}/{screen}"
        for module, project in projects.items()
        for screen, value in project.get("screens", {}).items()
        if not value.get("screen_id")
    ]
    assert not missing_ids, f"Telas Stitch sem screen_id: {missing_ids}"

    route_paths = set(re.findall(r'<Route path="([^"]+)"', app_source))
    home_modules = re.findall(r"\['([a-z_]+)', '[^']+', '[^']+', '[^']+'\]", home_source)
    assert len(home_modules) == 25, f"Home deve listar 25 modulos; encontrados {len(home_modules)}."
    missing_dashboards = [module for module in home_modules if f"/{module}" not in route_paths]
    assert not missing_dashboards, f"Cards sem dashboard real: {missing_dashboards}"

    assert "alert(" not in smart_crud, "SmartCRUD ainda contem alert demonstrativo."
    assert not re.search(r'<button(?:(?!>).)*(?:>|\s)\s*</button>', smart_crud, re.S), "Botao vazio encontrado."
    assert "onClick={() => {}}" not in smart_crud, "Botao com handler vazio encontrado."
    assert (APP / "public/_redirects").read_text().strip() == "/* /index.html 200"

    print(f"Frontend validado: {len(home_modules)} modulos, {screen_count} telas Stitch e fallback Cloudflare SPA.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
