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
    navigation = (APP / "src/components/Navigation.tsx").read_text()
    demo_data = (APP / "src/lib/demoData.ts").read_text()

    projects = sync.get("projects", {})
    screen_count = sum(len(project.get("screens", {})) for project in projects.values())
    assert len(projects) == manifest["project_count"] == 25, "Cobertura Stitch deve conter 25 projetos."
    assert manifest["screen_count"] >= 181, "Manifesto Stitch deve conter ao menos 181 telas."
    assert screen_count <= manifest["screen_count"], "Estado Stitch nao pode exceder o manifesto."

    missing_ids = [
        f"{module}/{screen}"
        for module, project in projects.items()
        for screen, value in project.get("screens", {}).items()
        if not value.get("screen_id")
    ]
    assert not missing_ids, f"Telas Stitch sem screen_id: {missing_ids}"

    route_paths = set(re.findall(r'<Route path="([^"]+)"', app_source))
    all_route_paths = re.findall(r'<Route path="([^"]+)"', app_source)
    duplicate_routes = sorted({path for path in all_route_paths if all_route_paths.count(path) > 1})
    assert not duplicate_routes, f"Rotas React duplicadas: {duplicate_routes}"
    navigation_paths = re.findall(r'path:\s*"([^"]+)"', navigation)
    missing_navigation_routes = sorted(set(navigation_paths) - route_paths)
    assert not missing_navigation_routes, f"Links da navegacao sem rota: {missing_navigation_routes}"
    assert len(navigation_paths) == len(set(navigation_paths)), "Navegacao contem links duplicados."
    home_modules = re.findall(r"\['([a-z_]+)', '[^']+', '[^']+', '[^']+'\]", home_source)
    assert len(home_modules) == 25, f"Home deve listar 25 modulos; encontrados {len(home_modules)}."
    missing_dashboards = [module for module in home_modules if f"/{module}" not in route_paths]
    assert not missing_dashboards, f"Cards sem dashboard real: {missing_dashboards}"

    assert "alert(" not in smart_crud, "SmartCRUD ainda contem alert demonstrativo."
    assert not re.search(r'<button(?:(?!>).)*(?:>|\s)\s*</button>', smart_crud, re.S), "Botao vazio encontrado."
    assert "onClick={() => {}}" not in smart_crud, "Botao com handler vazio encontrado."
    assert not (APP / "public/404.html").exists(), "Cloudflare Pages SPA exige ausencia de 404.html estatico."
    assert not (APP / "public/_redirects").exists(), "Fallback SPA automatico nao deve ter redirect circular."
    assert (APP / "public/_headers").is_file(), "Headers Cloudflare ausentes."
    wrangler = json.loads((APP / "wrangler.jsonc").read_text())
    assert wrangler.get("name") == "all-in-one-web"
    assert wrangler.get("pages_build_output_dir") == "./dist"

    scenario_block = demo_data.split("const MODULE_SCENARIOS", 1)[1].split("const STATUS", 1)[0]
    scenario_groups = re.findall(r"^\s{2}([a-z_]+): \[(.*?)\],$", scenario_block, re.MULTILINE)
    assert len(scenario_groups) == 25, f"Dados demo devem cobrir 25 modulos; encontrados {len(scenario_groups)}."
    invalid_counts = {module: len(re.findall(r"'[^']*'", values)) for module, values in scenario_groups if len(re.findall(r"'[^']*'", values)) != 10}
    assert not invalid_counts, f"Cada modulo deve conter dez cenarios: {invalid_counts}"
    module_media = APP / "public/assets/demo/modules"
    missing_media = [module for module, _ in scenario_groups if not (module_media / f"{module}.webp").is_file()]
    assert not missing_media, f"Modulos sem imagem demonstrativa: {missing_media}"
    assert (APP / "public/assets/demo/platform-overview.mp4").is_file(), "Video demonstrativo ausente."

    pending_screens = manifest["screen_count"] - screen_count
    print(
        f"Frontend validado: {len(home_modules)} modulos, {screen_count}/{manifest['screen_count']} telas Stitch, "
        f"{pending_screens} pendente(s) de sincronizacao remota, dez cenarios por modulo, midia local e fallback Cloudflare SPA."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
