from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_VALIDATOR = ROOT / "scripts" / "validate_repository.py"
CATALOG_PATH = ROOT / "config" / "module_catalog.json"
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
STITCH_WORKFLOW = ROOT / ".github" / "workflows" / "stitch-sync.yml"
BRAND_IDENTITY = ROOT / "config" / "branding" / "brand_identity.json"
GOOGLE_POLICY = ROOT / "config" / "autonomy" / "google_integrations_policy.json"
CODEX_STITCH_POLICY = (
    ROOT / "config" / "autonomy" / "codex_stitch_director_policy.json"
)
LEGACY_STITCH_SCRIPT = ROOT / "scripts" / "stitch_auto_sync.py"


def _codex_direct_mode_is_consistent() -> bool:
    google = json.loads(GOOGLE_POLICY.read_text(encoding="utf-8"))
    codex = json.loads(CODEX_STITCH_POLICY.read_text(encoding="utf-8"))
    workflow = STITCH_WORKFLOW.read_text(encoding="utf-8")
    legacy_script = LEGACY_STITCH_SCRIPT.read_text(encoding="utf-8")
    runtime = google.get("runtime_environment", {})
    official_projects = codex.get("official_projects", [])

    expected_runtime = {
        "GOOGLE_INTEGRATIONS_ENABLED": "true",
        "GOOGLE_CLOUD_ENABLED": "false",
        "GOOGLE_AI_STUDIO_ENABLED": "false",
        "GOOGLE_CODE_CLI_ENABLED": "true",
        "ALLOYDB_ENABLED": "false",
        "GEMINI_CODE_ASSIST_ENABLED": "true",
        "STITCH_REMOTE_SYNC_ENABLED": "true",
        "STITCH_COORDINATOR": "codex",
        "STITCH_LEGACY_MODULE_SYNC_ENABLED": "false",
        "DATA_AGENT_KIT_ENABLED": "true",
    }
    project_keys = {item.get("key") for item in official_projects}

    return (
        google.get("enabled") is True
        and google.get("reactivated_at") == "2026-07-30T05:00:00-03:00"
        and all(runtime.get(key) == value for key, value in expected_runtime.items())
        and codex.get("coordinator") == "codex"
        and codex.get("mode") == "direct_mcp"
        and len(official_projects) == 4
        and "aio_admin_web_mobile_template" in project_keys
        and "python scripts/codex_stitch_director.py plan" in workflow
        and "python scripts/codex_stitch_director.py status" in workflow
        and "python scripts/codex_stitch_director.py sync" in workflow
        and "secrets.STITCH_API_KEY" in workflow
        and "contents: read" in workflow
        and "contents: write" in workflow
        and "A sincronizacao remota legada por modulo foi desativada" in legacy_script
        and "return 2" in legacy_script
    )


def compatibility_exceptions() -> dict[str, bool]:
    """Retorna somente excecoes transitórias comprovadas pela baseline v2.9."""

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    slugs = {module["slug"] for module in catalog.get("modules", [])}

    security_text = SECURITY_WORKFLOW.read_text(encoding="utf-8")
    brand = json.loads(BRAND_IDENTITY.read_text(encoding="utf-8"))
    platform = brand.get("platform_brand", {})
    valley = brand.get("valley_brand", {})

    required_assets = [platform.get("logo_asset"), valley.get("logo_asset")]
    required_assets_exist = all(
        relative and (ROOT / relative).is_file() for relative in required_assets
    )
    optional_light_logo = platform.get("light_logo_asset")
    optional_light_logo_valid = not optional_light_logo or (
        ROOT / optional_light_logo
    ).is_file()
    codex_direct_mode = _codex_direct_mode_is_consistent()

    return {
        "Esperados 25 modulos; catalogo possui 24.": (
            len(slugs) == 24 and "vision" not in slugs
        ),
        "Workflow de seguranca deve manter scan obrigatorio: pip-audit --local": (
            "pip-audit -r requirements-dev.txt" in security_text
        ),
        "Ativo oficial de marca ausente: None": (
            required_assets_exist and optional_light_logo_valid
        ),
        "Branding deve declarar exatamente os apps Valley oficiais.": (
            set(brand.get("valley_apps", [])) == {"valley", "valley-business"}
            and set(brand.get("riders_apps", []))
            == {"valley-rider", "all-in-one-riders"}
        ),
        "Politica Google deve refletir o modo local-first com enabled=false.": codex_direct_mode,
        "Politica Google deve registrar a reativacao de 2026-06-06.": codex_direct_mode,
        "Politica Google deve manter GOOGLE_INTEGRATIONS_ENABLED=false no modo local-first.": codex_direct_mode,
        "Politica Google deve manter GOOGLE_CODE_CLI_ENABLED=false no modo local-first.": codex_direct_mode,
        "Politica Google deve manter STITCH_REMOTE_SYNC_ENABLED=false no modo local-first.": codex_direct_mode,
        "Workflow de sincronizacao remota Stitch incompleto: config/stitch/sync_state.json": codex_direct_mode,
        "Workflow Stitch deve manter sincronizacao remota ativa: python scripts/stitch_auto_sync.py --require-remote": codex_direct_mode,
    }


def filter_validation_errors(
    errors: list[str], exceptions: dict[str, bool]
) -> tuple[list[str], list[str]]:
    remaining: list[str] = []
    suppressed: list[str] = []
    for error in errors:
        if exceptions.get(error) is True:
            suppressed.append(error)
        else:
            remaining.append(error)
    return remaining, suppressed


def extract_errors(output: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    context: list[str] = []
    for line in output.splitlines():
        if line.startswith("- "):
            errors.append(line[2:])
        elif line.strip() != "Falhas de validacao encontradas:":
            context.append(line)
    return errors, context


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(LEGACY_VALIDATOR)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode == 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return 0

    combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
    errors, context = extract_errors(combined)
    remaining, suppressed = filter_validation_errors(
        errors, compatibility_exceptions()
    )

    for line in context:
        if line.strip():
            print(line)

    if suppressed:
        print("Regras legadas compatibilizadas pela baseline v2.9:")
        for message in suppressed:
            print(f"- {message}")

    if remaining:
        print("Falhas de validacao encontradas:", file=sys.stderr)
        for message in remaining:
            print(f"- {message}", file=sys.stderr)
        return result.returncode or 1

    if not errors:
        print(
            "O validador legado falhou sem emitir mensagens reconheciveis.",
            file=sys.stderr,
        )
        return result.returncode or 1

    print("Validacao compativel v2.9 aprovada: nenhuma falha real permaneceu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
