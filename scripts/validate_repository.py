from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_stitch_mcp_config import validate_stitch_mcp_config

CATALOG = json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))
STITCH_MANIFEST = ROOT / "config" / "stitch" / "screen_manifest.json"
STITCH_MCP_POLICY = ROOT / "config" / "autonomy" / "stitch_mcp_policy.json"
MULTI_AGENT_SYNC_POLICY = ROOT / "config" / "autonomy" / "multi_agent_sync_policy.json"
GOOGLE_INTEGRATIONS_POLICY = ROOT / "config" / "autonomy" / "google_integrations_policy.json"
GOOGLE_CLOUD_PROFILE = ROOT / "config" / "cloud" / "google_cloud_profile.json"
GOOGLE_CLOUD_INVENTORY = ROOT / "config" / "cloud" / "google_cloud_inventory.json"
STITCH_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "stitch-sync.yml"
BRAND_IDENTITY = ROOT / "config" / "branding" / "brand_identity.json"
COMPLIANCE_MATRIX = ROOT / "config" / "compliance" / "data_classification.json"
DATA_SUBJECT_RIGHTS = ROOT / "config" / "compliance" / "data_subject_rights.json"
RETENTION_JOBS = ROOT / "config" / "compliance" / "retention_jobs.json"
RETENTION_ALERTS = ROOT / "config" / "observability" / "retention_alerts.json"
PROVIDER_MATRIX = ROOT / "config" / "integrations" / "provider_matrix.json"
ENV_EXAMPLE = ROOT / ".env.example"
VSCODE_SETTINGS = ROOT / ".vscode" / "settings.json"
VSCODE_TASKS = ROOT / ".vscode" / "tasks.json"
DOCKER_COMPOSE = ROOT / "infra" / "docker" / "docker-compose.yml"
KUBERNETES_PLATFORM = ROOT / "infra" / "kubernetes" / "base" / "platform.yaml"
KUBERNETES_RETENTION_ALERTING = ROOT / "infra" / "kubernetes" / "base" / "retention-alerting.yaml"
REQUIRED_MODULE_FILES = {
    "README.md",
    "main.py",
    "requirements.txt",
    "CONTRACT.md",
    "STATUS.md",
    "OPENAPI.yaml",
    "DATABASE.md",
    "EVENTS.md",
    "SECURITY.md",
    "MONETIZATION.md",
    "TESTS.md",
    "Dockerfile",
    "tests/test_health.py",
    "tests/test_contract.py",
    "tests/test_permissions.py",
    "tests/test_create_flow.py",
}
REQUIRED_SCHEMAS = {
    "identity", "business", "permissions", "marketplace", "stock", "delivery",
    "services", "mobility", "erp", "wms", "tms", "crm", "bpm", "document",
    "finance", "billing", "fiscal", "hr", "health", "vision", "legal",
    "property", "audit", "compliance", "notifications", "api_hub",
    "insurance", "bi", "ai_core", "jobs",
}
REQUIRED_ENV_VARS = {
    "ALL_IN_ONE_POSTGRES_MATRIX_DSN",
    "ALL_IN_ONE_JOBS_POSTGRES_DSN",
    "ALL_IN_ONE_FINANCE_POSTGRES_DSN",
    "ALL_IN_ONE_IDENTITY_POSTGRES_DSN",
    "ALL_IN_ONE_RETENTION_POSTGRES_DSN",
    "ALL_IN_ONE_RETENTION_POLL_SECONDS",
    "GOOGLE_INTEGRATIONS_ENABLED",
    "GOOGLE_CLOUD_ENABLED",
    "GOOGLE_AI_STUDIO_ENABLED",
    "GOOGLE_CODE_CLI_ENABLED",
    "ALLOYDB_ENABLED",
    "GEMINI_CODE_ASSIST_ENABLED",
    "STITCH_REMOTE_SYNC_ENABLED",
}
REQUIRED_SUBJECT_RIGHTS = {
    "acesso",
    "correcao",
    "portabilidade",
    "anonimizacao",
    "revogacao de consentimento",
    "exclusao quando legalmente permitida",
}
REQUIRED_RETENTION_JOBS = {
    "retention_review_daily",
    "anonymization_worker_hourly",
    "deletion_worker_daily",
    "legal_hold_reconciliation_daily",
}
REQUIRED_RETENTION_ALERTS = {
    "RetentionCronJobFailed",
    "RetentionCronJobDelayed",
    "RetentionBacklogHigh",
    "RetentionOldestCandidateTooOld",
    "RetentionDecisionMissing",
}
REQUIRED_MULTI_AGENT_IDS = {
    "codex_cli",
    "antigravity",
    "gemini_code",
    "gemini_cli_termux",
    "gemini_cli_ubuntu",
}
REQUIRED_MULTI_AGENT_RULES = [
    "Git como fonte de verdade",
    "git reset --hard",
    "STITCH_API_KEY",
    "config/stitch/sync_state.json",
    "STATUS.md",
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    modules = CATALOG["modules"]
    slugs = {module["slug"] for module in modules}
    if len(slugs) != 25:
        fail(f"Esperados 25 modulos; catalogo possui {len(slugs)}.", errors)
    for module in modules:
        base = ROOT / "modules" / module["slug"]
        for relative in REQUIRED_MODULE_FILES:
            if not (base / relative).is_file():
                fail(f"Ausente: modules/{module['slug']}/{relative}", errors)
        if not (ROOT / "contracts" / f"{module['slug']}.md").is_file():
            fail(f"Contrato ausente: {module['slug']}", errors)
    for app in CATALOG["apps"]:
        if not (ROOT / "apps" / app["slug"] / "README.md").is_file():
            fail(f"App ausente: {app['slug']}", errors)
    migrations = "\n".join(
        item.read_text(encoding="utf-8")
        for item in sorted((ROOT / "database" / "postgres" / "migrations").glob("*.sql"))
    )
    for schema in REQUIRED_SCHEMAS:
        if f"CREATE SCHEMA IF NOT EXISTS {schema}" not in migrations:
            fail(f"Schema PostgreSQL nao declarado: {schema}", errors)
    env_example = ENV_EXAMPLE.read_text(encoding="utf-8") if ENV_EXAMPLE.is_file() else ""
    if not env_example:
        fail("Contrato de variaveis ausente: .env.example", errors)
    for env_var in REQUIRED_ENV_VARS:
        if f"{env_var}=" not in env_example:
            fail(f"Variavel de ambiente obrigatoria nao declarada em .env.example: {env_var}", errors)
    for needle in [
        "identity.users",
        "finance.wallets",
        "delivery.rider_documents",
        "delivery.rider_reviews",
        "NUMERIC(18, 4)",
        "NUMERIC(18, 8)",
        "reject_immutable_change",
        "audit.logs",
        "jobs.resumes",
        "employment_provenance_integrity",
        "immutable_jobs_resume_access_logs",
        "storage_encryption",
        "idx_jobs_documents_idempotency",
        "compliance.retention_candidates",
        "compliance.retention_decisions",
        "idx_retention_candidates_status",
        "idx_outbox_dispatcher_ready",
        "idx_finance_ledger_wallet_lookup",
        "idx_audit_events_correlation",
        "idx_finance_gold_ledger_entity_lookup",
        "idx_jobs_resumes_visibility",
        "idx_business_membership_lookup",
        "erp.invoice_items",
        "idx_invoice_items_document",
    ]:
        if needle not in migrations:
            fail(f"Controle SQL ausente: {needle}", errors)
    for workflow in [
        "ci.yml",
        "security.yml",
        "database.yml",
        "openapi.yml",
        "autocommit.yml",
        "automerge.yml",
        "compose-health.yml",
        "git-sync.yml",
        "stitch-sync.yml",
    ]:
        if not (ROOT / ".github" / "workflows" / workflow).is_file():
            fail(f"Workflow ausente: {workflow}", errors)
    for script in [
        "check_git_sync.ps1",
        "check_git_sync.py",
        "validate_compose_health.ps1",
        "validate_compose_health.py",
        "check_generated_artifacts.ps1",
        "check_generated_artifacts.py",
        "multi_agent_sync_guard.py",
    ]:
        if not (ROOT / "scripts" / script).is_file():
            fail(f"Gate operacional ausente: {script}", errors)
    if not (ROOT / "pytest.ini").is_file():
        fail("Configuracao pytest.ini ausente.", errors)
    else:
        pytest_ini = (ROOT / "pytest.ini").read_text(encoding="utf-8")
        if "--import-mode=importlib" not in pytest_ini or "--basetemp=.pytest_tmp" not in pytest_ini:
            fail("pytest.ini deve centralizar importlib e basetemp local .pytest_tmp.", errors)
    dockerignore_path = ROOT / ".dockerignore"
    if not dockerignore_path.is_file():
        fail(".dockerignore ausente; builds Docker devem excluir caches, .venv e artefatos locais pesados.", errors)
    else:
        dockerignore = dockerignore_path.read_text(encoding="utf-8")
        for ignored_path in [".git", ".venv", ".pytest_cache", ".pytest_tmp", "node_modules", "tests", "apps"]:
            if ignored_path not in dockerignore:
                fail(f".dockerignore deve excluir {ignored_path} do contexto Docker.", errors)
    if not VSCODE_SETTINGS.is_file():
        fail("Configuracao VS Code ausente: .vscode/settings.json", errors)
    else:
        settings = json.loads(VSCODE_SETTINGS.read_text(encoding="utf-8"))
        expected_python = "${workspaceFolder}/.venv/bin/python"
        if settings.get("python.defaultInterpreterPath") != expected_python:
            fail(f"python.defaultInterpreterPath deve ser {expected_python}. Corrija no .vscode/settings.json e execute python -m venv .venv", errors)
        if settings.get("python.testing.pytestArgs") not in ([], None):
            fail("python.testing.pytestArgs deve ficar vazio; pytest.ini e a fonte obrigatoria.", errors)
        if settings.get("mdb.presetConnections") not in ([], None):
            fail("mdb.presetConnections deve ficar vazio para nao tentar conectar automaticamente ao Mongo local.", errors)
        if settings.get("geminicodeassist.outlines.automaticOutlineGeneration") is not True:
            fail("Gemini Code Assist deve permanecer ativo no Antigravity/editor.", errors)
        if settings.get("geminicodeassist.enable") is not True:
            fail("geminicodeassist.enable deve permanecer true no Antigravity/editor.", errors)
        if settings.get("geminicodeassist.agentYoloMode") is not False:
            fail("geminicodeassist.agentYoloMode deve permanecer false para evitar execucao destrutiva automatica.", errors)
    vscode_extensions = ROOT / ".vscode" / "extensions.json"
    if not vscode_extensions.is_file():
        fail("Configuracao VS Code ausente: .vscode/extensions.json", errors)
    else:
        extensions = json.loads(vscode_extensions.read_text(encoding="utf-8"))
        recommendations = set(extensions.get("recommendations", []))
        for extension in ["ms-python.python", "ms-python.vscode-pylance", "ms-python.debugpy"]:
            if extension not in recommendations:
                fail(f"Extensao VS Code Python obrigatoria ausente em .vscode/extensions.json: {extension}", errors)
    if not VSCODE_TASKS.is_file():
        fail("Configuracao VS Code ausente: .vscode/tasks.json", errors)
    else:
        tasks = json.loads(VSCODE_TASKS.read_text(encoding="utf-8"))
        pytest_tasks = [task for task in tasks.get("tasks", []) if task.get("label") == "test: pytest completo"]
        if not pytest_tasks:
            fail("Task VS Code test: pytest completo ausente.", errors)
        elif pytest_tasks[0].get("command") != "${config:python.defaultInterpreterPath}":
            fail("Task pytest deve usar ${config:python.defaultInterpreterPath}.", errors)
    if not (ROOT / "workers" / "outbox_dispatcher" / "main.py").is_file():
        fail("Worker da outbox RabbitMQ ausente.", errors)
    for relative in ["workers/retention_worker/main.py", "modules/shared/retention_worker.py"]:
        if not (ROOT / relative).is_file():
            fail(f"Worker de retencao LGPD ausente: {relative}", errors)
    compose = DOCKER_COMPOSE.read_text(encoding="utf-8") if DOCKER_COMPOSE.is_file() else ""
    if "retention-worker:" not in compose or "workers/retention_worker/Dockerfile" not in compose:
        fail("Docker Compose deve agendar o worker de retencao LGPD.", errors)
    if "deletion_worker_daily --dry-run" not in compose:
        fail("Docker Compose deve manter descarte LGPD em dry-run ate homologacao por modulo.", errors)
    for active_env in [
        'GOOGLE_INTEGRATIONS_ENABLED: "${GOOGLE_INTEGRATIONS_ENABLED:-false}"',
        'GOOGLE_CLOUD_ENABLED: "${GOOGLE_CLOUD_ENABLED:-false}"',
        'GOOGLE_AI_STUDIO_ENABLED: "${GOOGLE_AI_STUDIO_ENABLED:-false}"',
        'GOOGLE_CODE_CLI_ENABLED: "${GOOGLE_CODE_CLI_ENABLED:-false}"',
        'ALLOYDB_ENABLED: "${ALLOYDB_ENABLED:-false}"',
        'ALLOYDB_DSN: "${ALLOYDB_DSN:-}"',
        'GEMINI_CODE_ASSIST_ENABLED: "true"',
        'STITCH_REMOTE_SYNC_ENABLED: "${STITCH_REMOTE_SYNC_ENABLED:-false}"',
    ]:
        if active_env not in compose:
            fail(f"Docker Compose deve manter o contrato local-first com coordenada futura Google: {active_env}", errors)
    kubernetes = "\n".join(
        manifest.read_text(encoding="utf-8")
        for manifest in sorted(KUBERNETES_PLATFORM.parent.glob("*.yaml"))
    )
    if "kind: CronJob" not in kubernetes or "name: retention-worker" not in kubernetes:
        fail("Kubernetes deve declarar CronJob retention-worker.", errors)
    if "ALL_IN_ONE_RETENTION_POSTGRES_DSN" not in kubernetes:
        fail("CronJob de retencao deve receber DSN por Secret/Vault.", errors)
    if not STITCH_MANIFEST.is_file():
        fail("Manifesto de telas Stitch ausente.", errors)
    else:
        stitch = json.loads(STITCH_MANIFEST.read_text(encoding="utf-8"))
        projects = stitch.get("projects", [])
        if stitch.get("project_count") != len(modules) or len(projects) != len(modules):
            fail("Stitch deve declarar um projeto por modulo.", errors)
        if not all(project.get("screen_count", 0) > 0 for project in projects):
            fail("Todo projeto Stitch deve declarar telas.", errors)
        if stitch.get("branding_source") != "config/branding/brand_identity.json":
            fail("Manifesto Stitch deve declarar a fonte de branding oficial.", errors)
    if not BRAND_IDENTITY.is_file():
        fail("Contrato de branding oficial ausente: config/branding/brand_identity.json", errors)
    else:
        brand = json.loads(BRAND_IDENTITY.read_text(encoding="utf-8"))
        for relative in [
            brand.get("platform_brand", {}).get("logo_asset"),
            brand.get("platform_brand", {}).get("light_logo_asset"),
            brand.get("valley_brand", {}).get("logo_asset"),
        ]:
            if not relative or not (ROOT / relative).is_file():
                fail(f"Ativo oficial de marca ausente: {relative}", errors)
        if set(brand.get("valley_apps", [])) != {"valley", "valley-business", "valley-rider"}:
            fail("Branding deve declarar exatamente os apps Valley oficiais.", errors)
    if not STITCH_MCP_POLICY.is_file():
        fail("Politica obrigatoria do MCP Stitch ausente.", errors)
    else:
        for error in validate_stitch_mcp_config(require_secret=False, require_codex_config=False):
            fail(error, errors)
        stitch_policy = json.loads(STITCH_MCP_POLICY.read_text(encoding="utf-8"))
        if stitch_policy.get("enabled") is not True:
            fail("Politica Stitch deve permanecer enabled=true.", errors)
        if stitch_policy.get("reactivated_at") != "2026-06-06":
            fail("Politica Stitch deve registrar a reativacao de 2026-06-06.", errors)
    if not GOOGLE_INTEGRATIONS_POLICY.is_file():
        fail("Politica obrigatoria de integracoes Google ausente.", errors)
    else:
        google_policy = json.loads(GOOGLE_INTEGRATIONS_POLICY.read_text(encoding="utf-8"))
        if google_policy.get("enabled") is not False:
            fail("Politica Google deve refletir o modo local-first com enabled=false.", errors)
        if google_policy.get("reactivated_at") != "2026-06-06":
            fail("Politica Google deve registrar a reativacao de 2026-06-06.", errors)
        expected_integrations = {
            "google_sdk",
            "google_ai_studio",
            "google_cloud",
            "alloydb",
            "google_code_cli",
            "gemini_cli_termux",
            "gemini_cli_ubuntu",
            "google_stitch_mcp",
        }
        if set(google_policy.get("affected_integrations", [])) != expected_integrations:
            fail("Politica Google deve cobrir SDK, AI Studio, Cloud, AlloyDB, Code CLI e Gemini CLI.", errors)
        runtime = google_policy.get("runtime_environment", {})
        active_variables = [
            "GOOGLE_INTEGRATIONS_ENABLED",
            "GOOGLE_CLOUD_ENABLED",
            "GOOGLE_AI_STUDIO_ENABLED",
            "GOOGLE_CODE_CLI_ENABLED",
            "ALLOYDB_ENABLED"
        ]
        for variable in active_variables:
            if runtime.get(variable) != "false":
                fail(f"Politica Google deve manter {variable}=false no modo local-first.", errors)
        if runtime.get("GEMINI_CODE_ASSIST_ENABLED") != "true":
            fail("Politica Google deve manter GEMINI_CODE_ASSIST_ENABLED=true no Antigravity/editor.", errors)
        if runtime.get("STITCH_REMOTE_SYNC_ENABLED") != "false":
            fail("Politica Google deve manter STITCH_REMOTE_SYNC_ENABLED=false no modo local-first.", errors)
    if not GOOGLE_CLOUD_PROFILE.is_file():
        fail("Perfil Google Cloud ativo ausente: config/cloud/google_cloud_profile.json", errors)
    else:
        cloud_profile = json.loads(GOOGLE_CLOUD_PROFILE.read_text(encoding="utf-8"))
        if cloud_profile.get("enabled") is not True:
            fail("Perfil Google Cloud deve permanecer enabled=true.", errors)
        required_apis = set(cloud_profile.get("required_apis", []))
        for required_api in {"aiplatform.googleapis.com", "alloydb.googleapis.com", "run.googleapis.com"}:
            if required_api not in required_apis:
                fail(f"Perfil Google Cloud deve habilitar {required_api}.", errors)
        safety = cloud_profile.get("safety", {})
        for forbidden in ["allow_delete", "allow_billing_change", "allow_policy_bypass"]:
            if safety.get(forbidden) is not False:
                fail(f"Perfil Google Cloud deve manter {forbidden}=false.", errors)
        if cloud_profile.get("authoritative_project") != "all-in-one-498012":
            fail("Perfil Google Cloud deve apontar para o projeto autoritativo all-in-one-498012.", errors)
        if cloud_profile.get("authority_mode") != "remote_state_is_authoritative":
            fail("Perfil Google Cloud deve tratar o estado remoto como autoritativo.", errors)
        if safety.get("requires_import_before_change") is not True:
            fail("Perfil Google Cloud deve exigir importacao antes de mudancas.", errors)
    if not GOOGLE_CLOUD_INVENTORY.is_file():
        fail("Inventario Google Cloud autoritativo ausente.", errors)
    else:
        cloud_inventory = json.loads(GOOGLE_CLOUD_INVENTORY.read_text(encoding="utf-8"))
        authority = cloud_inventory.get("authority", {})
        security = cloud_inventory.get("security", {})
        if authority.get("project_id") != "all-in-one-498012":
            fail("Inventario Google Cloud deve pertencer a all-in-one-498012.", errors)
        if authority.get("mode") != "remote_state_is_authoritative":
            fail("Inventario Google Cloud deve declarar autoridade remota.", errors)
        if any(security.get(flag) is not False for flag in ["secrets_included", "api_key_values_included", "service_account_private_keys_included", "kms_key_material_included"]):
            fail("Inventario Google Cloud nao pode incluir segredos ou material criptografico.", errors)
    if not PROVIDER_MATRIX.is_file():
        fail("Matriz de provedores ausente: config/integrations/provider_matrix.json", errors)
    else:
        provider_matrix = json.loads(PROVIDER_MATRIX.read_text(encoding="utf-8"))
        integrations = {item.get("key"): item for item in provider_matrix.get("integrations", [])}
        maps = integrations.get("maps_routing_tracking", {})
        active_maps = set(maps.get("primary_candidates", [])) | set(maps.get("fallback_candidates", []))
        if "Google Maps Platform" not in active_maps:
            fail("Google Maps Platform deve permanecer entre os candidatos ativos.", errors)
        ai_agent = integrations.get("ai_agent_superdesign", {})
        if not str(ai_agent.get("primary_model", "")).lower().startswith("google/"):
            fail("Modelo primario do agente AI deve usar Google/Gemini apos a reativacao.", errors)
        active_ai = set(ai_agent.get("primary_candidates", [])) | set(ai_agent.get("fallback_candidates", []))
        if "Google Gemini API" not in active_ai:
            fail("Google Gemini API deve permanecer entre os candidatos ativos.", errors)
    if not MULTI_AGENT_SYNC_POLICY.is_file():
        fail("Politica obrigatoria de alinhamento multiagente ausente.", errors)
    else:
        multi_agent_policy = json.loads(MULTI_AGENT_SYNC_POLICY.read_text(encoding="utf-8"))
        if multi_agent_policy.get("enabled") is not True:
            fail("Politica multiagente deve estar habilitada.", errors)
        if multi_agent_policy.get("language") != "pt-BR":
            fail("Politica multiagente deve manter idioma pt-BR.", errors)
        source_of_truth = multi_agent_policy.get("source_of_truth", {})
        if source_of_truth.get("repository") != "git" or source_of_truth.get("preferred_push_remote") != "fork":
            fail("Politica multiagente deve declarar Git e remoto fork como contrato de sincronizacao.", errors)
        agent_ids = {agent.get("id") for agent in multi_agent_policy.get("agents", [])}
        if agent_ids != REQUIRED_MULTI_AGENT_IDS:
            fail("Politica multiagente deve cobrir Codex CLI, Antigravity, Gemini Code e Gemini CLI Termux/Ubuntu.", errors)
        enabled_agents = {
            agent.get("id")
            for agent in multi_agent_policy.get("agents", [])
            if agent.get("enabled") is True
        }
        if not {"gemini_code", "gemini_cli_termux", "gemini_cli_ubuntu"}.issubset(enabled_agents):
            fail("Gemini Code Assist e Gemini CLI Termux/Ubuntu devem permanecer ativos.", errors)
        mandatory_rules = "\n".join(multi_agent_policy.get("mandatory_rules", []))
        for needle in REQUIRED_MULTI_AGENT_RULES:
            if needle not in mandatory_rules:
                fail(f"Politica multiagente incompleta: {needle}", errors)
        stitch_alignment = multi_agent_policy.get("stitch_alignment", {})
        if stitch_alignment.get("state") != "config/stitch/sync_state.json" or stitch_alignment.get("remote_secret") != "STITCH_API_KEY":
            fail("Politica multiagente deve preservar estado Stitch e segredo remoto oficial.", errors)
        if stitch_alignment.get("enabled") is not True:
            fail("Alinhamento Stitch remoto deve permanecer ativo na politica multiagente.", errors)
        coordination_guard = multi_agent_policy.get("coordination_guard", {})
        if coordination_guard.get("script") != "scripts/multi_agent_sync_guard.py":
            fail("Politica multiagente deve apontar para o guardiao de coordenacao versionado.", errors)
        if coordination_guard.get("required_before_edit") is not True:
            fail("Guardiao multiagente deve ser obrigatorio antes de editar.", errors)
        pre_work_commands = "\n".join(multi_agent_policy.get("pre_work_commands", []))
        if "multi_agent_sync_guard.py preflight --integrate" not in pre_work_commands:
            fail("Politica multiagente deve executar preflight remoto antes da edicao.", errors)
        if "multi_agent_sync_guard.py acquire" not in pre_work_commands:
            fail("Politica multiagente deve adquirir lock antes da edicao.", errors)
    for agent_contract in ["AGENTS.md", "GEMINI.md"]:
        contract_text = (ROOT / agent_contract).read_text(encoding="utf-8") if (ROOT / agent_contract).is_file() else ""
        if "config/autonomy/multi_agent_sync_policy.json" not in contract_text:
            fail(f"{agent_contract} deve referenciar a politica multiagente obrigatoria.", errors)
    antigravity_config = ROOT / ".agents" / "antigravity.json"
    if not antigravity_config.is_file():
        fail("Contrato Antigravity ausente: .agents/antigravity.json", errors)
    else:
        antigravity = json.loads(antigravity_config.read_text(encoding="utf-8"))
        if antigravity.get("name") != "antigravity":
            fail("Contrato Antigravity deve declarar name=antigravity.", errors)
        required_mcp_servers = {"docker", "playwright"}
        if not required_mcp_servers.issubset(set(antigravity.get("mcp_servers", []))):
            fail("Contrato Antigravity deve manter MCPs essenciais ativos: docker e playwright.", errors)
        if "stitch" not in set(antigravity.get("mcp_servers", [])):
            fail("Antigravity deve manter o MCP Stitch ativo.", errors)
    stitch_workflow = STITCH_SYNC_WORKFLOW.read_text(encoding="utf-8") if STITCH_SYNC_WORKFLOW.is_file() else ""
    for needle in [
        "workflow_dispatch:",
        "secrets.STITCH_API_KEY",
        "config/stitch/sync_state.json",
    ]:
        if needle not in stitch_workflow:
            fail(f"Workflow de sincronizacao remota Stitch incompleto: {needle}", errors)
    for active_trigger in [
        "  push:",
        "  schedule:",
        'STITCH_REMOTE_SYNC_ENABLED: "true"',
        "python scripts/stitch_auto_sync.py --require-remote",
    ]:
        if active_trigger not in stitch_workflow:
            fail(f"Workflow Stitch deve manter sincronizacao remota ativa: {active_trigger}", errors)
    if "if: ${{ false }}" in stitch_workflow:
        fail("Workflow Stitch nao pode manter o job explicitamente desativado.", errors)
    if not (ROOT / "docs" / "COMPLIANCE.md").is_file():
        fail("Documento de compliance ausente: docs/COMPLIANCE.md", errors)
    if not COMPLIANCE_MATRIX.is_file():
        fail(f"Matriz de dados sensiveis ausente: {COMPLIANCE_MATRIX}", errors)
    else:
        compliance = json.loads(COMPLIANCE_MATRIX.read_text(encoding="utf-8"))
        if set(compliance.get("modules", {})) != slugs:
            fail("Matriz de compliance deve cobrir exatamente os 25 modulos do catalogo.", errors)
        if set(compliance.get("policy", {}).get("subject_rights", [])) != REQUIRED_SUBJECT_RIGHTS:
            fail("Politica de compliance deve declarar todos os direitos do titular.", errors)
        for slug, entry in compliance.get("modules", {}).items():
            for field in ["risk_level", "data_domains", "sensitive_categories", "legal_basis", "retention_policy", "production_gate"]:
                if not entry.get(field):
                    fail(f"Matriz de compliance incompleta em {slug}.{field}.", errors)
    if not DATA_SUBJECT_RIGHTS.is_file():
        fail(f"Fluxo de direitos do titular ausente: {DATA_SUBJECT_RIGHTS}", errors)
    else:
        subject_rights = json.loads(DATA_SUBJECT_RIGHTS.read_text(encoding="utf-8"))
        if set(subject_rights.get("rights", {})) != REQUIRED_SUBJECT_RIGHTS:
            fail("Fluxo de direitos do titular deve cobrir todos os direitos LGPD versionados.", errors)
        if set(subject_rights.get("module_coverage", {})) != slugs:
            fail("Fluxo de direitos do titular deve cobrir exatamente os 25 modulos do catalogo.", errors)
        guardrails = subject_rights.get("guardrails", {})
        if guardrails.get("audit_event") != "compliance.data_subject_request.processed":
            fail("Fluxo de direitos do titular deve declarar evento auditavel padrao.", errors)
    if not RETENTION_JOBS.is_file():
        fail(f"Contrato de jobs de retencao ausente: {RETENTION_JOBS}", errors)
    else:
        retention_jobs = json.loads(RETENTION_JOBS.read_text(encoding="utf-8"))
        if set(retention_jobs.get("jobs", {})) != REQUIRED_RETENTION_JOBS:
            fail("Jobs de retencao devem declarar revisao, anonimizacao, descarte e legal hold.", errors)
        if set(retention_jobs.get("module_rules", {})) != slugs:
            fail("Jobs de retencao devem cobrir exatamente os 25 modulos do catalogo.", errors)
        safety = retention_jobs.get("safety_rules", {})
        if not safety.get("requires_subject_rights_link") or not safety.get("requires_immutable_audit"):
            fail("Jobs de retencao devem exigir vinculo com direitos do titular e auditoria imutavel.", errors)
    if not RETENTION_ALERTS.is_file():
        fail(f"Contrato de alertas de retencao ausente: {RETENTION_ALERTS}", errors)
    else:
        retention_alerts = json.loads(RETENTION_ALERTS.read_text(encoding="utf-8"))
        if set(retention_alerts.get("alerts", {})) != REQUIRED_RETENTION_ALERTS:
            fail("Alertas de retencao devem cobrir falha, atraso, backlog, idade e ausencia de decisao.", errors)
        if retention_alerts.get("notification_policy", {}).get("include_sensitive_payload") is not False:
            fail("Alertas de retencao nao podem incluir payload sensivel.", errors)
        for alert_name, alert in retention_alerts.get("alerts", {}).items():
            if not alert.get("expr") or not alert.get("evidence") or "incident_ticket" not in alert.get("evidence", []):
                fail(f"Alerta de retencao incompleto: {alert_name}", errors)
        retention_alerting = KUBERNETES_RETENTION_ALERTING.read_text(encoding="utf-8") if KUBERNETES_RETENTION_ALERTING.is_file() else ""
        if "kind: PrometheusRule" not in retention_alerting or "kind: AlertmanagerConfig" not in retention_alerting:
            fail("Alertas de retencao devem ter PrometheusRule e AlertmanagerConfig Kubernetes.", errors)
        for alert_name, alert in retention_alerts.get("alerts", {}).items():
            if f"alert: {alert_name}" not in retention_alerting or alert["expr"] not in retention_alerting:
                fail(f"PrometheusRule de retencao nao materializa alerta: {alert_name}", errors)

    if errors:
        print("\nFalhas de validacao encontradas:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nRepositorio validado com sucesso! Todos os 25 modulos e infraestrutura estao em conformidade.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
