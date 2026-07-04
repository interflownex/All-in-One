from __future__ import annotations

import json
import re
import sys
import uuid
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
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
BRAND_IDENTITY = ROOT / "config" / "branding" / "brand_identity.json"
COMPLIANCE_MATRIX = ROOT / "config" / "compliance" / "data_classification.json"
DATA_SUBJECT_RIGHTS = ROOT / "config" / "compliance" / "data_subject_rights.json"
RETENTION_JOBS = ROOT / "config" / "compliance" / "retention_jobs.json"
RETENTION_ALERTS = ROOT / "config" / "observability" / "retention_alerts.json"
OUTBOX_ALERTS = ROOT / "config" / "observability" / "outbox_alerts.json"
OUTBOX_DASHBOARD = ROOT / "config" / "observability" / "outbox_dashboard.json"
DOMAIN_EVENT_FIXTURES = ROOT / "config" / "events" / "domain_event_fixtures.json"
EVENTS_DOC = ROOT / "docs" / "EVENTS.md"
PROVIDER_MATRIX = ROOT / "config" / "integrations" / "provider_matrix.json"
ENV_EXAMPLE = ROOT / ".env.example"
VSCODE_SETTINGS = ROOT / ".vscode" / "settings.json"
VSCODE_TASKS = ROOT / ".vscode" / "tasks.json"
DOCKER_COMPOSE = ROOT / "infra" / "docker" / "docker-compose.yml"
KUBERNETES_PLATFORM = ROOT / "infra" / "kubernetes" / "base" / "platform.yaml"
KUBERNETES_KUSTOMIZATION = ROOT / "infra" / "kubernetes" / "base" / "kustomization.yaml"
KUBERNETES_OUTBOX_ALERTING = ROOT / "infra" / "kubernetes" / "base" / "outbox-alerting.yaml"
KUBERNETES_OUTBOX_DASHBOARD = ROOT / "infra" / "kubernetes" / "base" / "outbox-dashboard.yaml"
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
REQUIRED_OUTBOX_ALERTS = {
    "OutboxPublishStalled",
    "OutboxBacklogHigh",
    "OutboxDueHigh",
    "OutboxRetryFailuresHigh",
    "OutboxOldestPendingTooOld",
}
REQUIRED_OUTBOX_DASHBOARD_TITLES = {
    "Pendentes",
    "Prontos para retry",
    "Publicados",
    "Falhas retryable",
    "Maior retry observado",
    "Idade do pendente mais antigo",
    "Tendencia do backlog",
    "Tendencia de publicacoes e falhas",
}
REQUIRED_OUTBOX_DASHBOARD_METRICS = {
    "all_in_one_outbox_pending",
    "all_in_one_outbox_due",
    "all_in_one_outbox_published_total",
    "all_in_one_outbox_failed_retryable_total",
    "all_in_one_outbox_max_retry_count",
    "all_in_one_outbox_oldest_pending_age_seconds",
}
EVENT_BULLET_PATTERN = re.compile(r"^\s*-\s*`([^`]+)`\s*$", re.MULTILINE)
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


def extract_event_keys(text: str) -> list[str]:
    return EVENT_BULLET_PATTERN.findall(text)


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
        module_events_doc = base / "EVENTS.md"
        if not module_events_doc.is_file():
            fail(f"EVENTS.md ausente: modules/{module['slug']}/EVENTS.md", errors)
        else:
            module_doc_events = extract_event_keys(module_events_doc.read_text(encoding="utf-8"))
            if module_doc_events != module.get("events", []):
                fail(f"EVENTS.md de {module['slug']} nao bate com o catalogo de eventos.", errors)
    events_doc = EVENTS_DOC.read_text(encoding="utf-8") if EVENTS_DOC.is_file() else ""
    if not events_doc:
        fail("Documento de eventos ausente: docs/EVENTS.md", errors)
    elif "valley.gold.ledger.posted" not in events_doc:
        fail("docs/EVENTS.md deve documentar o evento valley.gold.ledger.posted.", errors)
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
        "repair-loop.yml",
        "stitch-sync.yml",
    ]:
        if not (ROOT / ".github" / "workflows" / workflow).is_file():
            fail(f"Workflow ausente: {workflow}", errors)
    security_workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8") if SECURITY_WORKFLOW.is_file() else ""
    for needle in [
        "matrix:",
        "pip-audit --local",
        "bandit -r modules/shared scripts workers -q -ll",
        "python -m pytest -q tests/test_security_gates.py",
        "modules/api_hub/Dockerfile",
        "modules/identity/Dockerfile",
        "modules/jobs/Dockerfile",
        "all-in-one-api-hub:security",
        "all-in-one-identity:security",
        "all-in-one-jobs:security",
        "aquasecurity/trivy-action",
        "severity: HIGH,CRITICAL",
        "ignore-unfixed: true",
    ]:
        if needle not in security_workflow:
            fail(f"Workflow de seguranca incompleto: {needle}", errors)
    for script in [
        "check_git_sync.ps1",
        "validate_compose_health.ps1",
        "check_generated_artifacts.ps1",
        "check_generated_artifacts.py",
        "multi_agent_sync_guard.py",
        "repair_actions_loop.py",
    ]:
        if not (ROOT / "scripts" / script).is_file():
            fail(f"Gate operacional ausente: {script}", errors)
    if not (ROOT / "pytest.ini").is_file():
        fail("Configuracao pytest.ini ausente.", errors)
    else:
        pytest_ini = (ROOT / "pytest.ini").read_text(encoding="utf-8")
        if "--import-mode=importlib" not in pytest_ini or "--basetemp=.pytest_tmp" not in pytest_ini:
            fail("pytest.ini deve centralizar importlib e basetemp local .pytest_tmp.", errors)
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
        repair_tasks = [task for task in tasks.get("tasks", []) if task.get("label") == "repair: loop github actions"]
        if not repair_tasks:
            fail("Task VS Code repair: loop github actions ausente.", errors)
        elif repair_tasks[0].get("command") != "${config:python.defaultInterpreterPath}":
            fail("Task repair loop deve usar ${config:python.defaultInterpreterPath}.", errors)
        else:
            repair_args = repair_tasks[0].get("args", [])
            if repair_args[:1] != ["scripts/repair_actions_loop.py"] or "--continuous" not in repair_args:
                fail("Task repair loop deve executar scripts/repair_actions_loop.py --continuous.", errors)
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
        'GOOGLE_INTEGRATIONS_ENABLED: "${GOOGLE_INTEGRATIONS_ENABLED:-true}"',
        'GOOGLE_CLOUD_ENABLED: "${GOOGLE_CLOUD_ENABLED:-true}"',
        'GOOGLE_AI_STUDIO_ENABLED: "${GOOGLE_AI_STUDIO_ENABLED:-true}"',
        'GOOGLE_CODE_CLI_ENABLED: "${GOOGLE_CODE_CLI_ENABLED:-true}"',
        'ALLOYDB_ENABLED: "${ALLOYDB_ENABLED:-true}"',
        'ALLOYDB_DSN: "${ALLOYDB_DSN:-}"',
        'GEMINI_CODE_ASSIST_ENABLED: "true"',
        'STITCH_REMOTE_SYNC_ENABLED: "${STITCH_REMOTE_SYNC_ENABLED:-true}"',
    ]:
        if active_env not in compose:
            fail(f"Docker Compose deve manter integracao Google ativa: {active_env}", errors)
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
        if google_policy.get("enabled") is not True:
            fail("Politica Google deve permanecer enabled=true.", errors)
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
            if runtime.get(variable) != "true":
                fail(f"Politica Google deve manter {variable}=true.", errors)
        if runtime.get("GEMINI_CODE_ASSIST_ENABLED") != "true":
            fail("Politica Google deve manter GEMINI_CODE_ASSIST_ENABLED=true no Antigravity/editor.", errors)
        if runtime.get("STITCH_REMOTE_SYNC_ENABLED") != "true":
            fail("Politica Google deve manter STITCH_REMOTE_SYNC_ENABLED=true.", errors)
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
    repair_loop_workflow = (ROOT / ".github" / "workflows" / "repair-loop.yml").read_text(encoding="utf-8") if (ROOT / ".github" / "workflows" / "repair-loop.yml").is_file() else ""
    for needle in [
        "workflow_dispatch:",
        "continuous:",
        "push:",
        "pull_request:",
        "schedule:",
        "contents: write",
        "pull-requests: write",
        "scripts/repair_actions_loop.py",
        "--continuous",
        "--max-cycles 1",
        "GH_TOKEN: ${{ github.token }}",
    ]:
        if needle not in repair_loop_workflow:
            fail(f"Workflow de repair loop incompleto: {needle}", errors)
    if not (ROOT / "docs" / "COMPLIANCE.md").is_file():
        fail("Documento de compliance ausente: docs/COMPLIANCE.md", errors)
    if not KUBERNETES_KUSTOMIZATION.is_file():
        fail("Kustomization base ausente: infra/kubernetes/base/kustomization.yaml", errors)
    else:
        kustomization = KUBERNETES_KUSTOMIZATION.read_text(encoding="utf-8")
        if "outbox-alerting.yaml" not in kustomization:
            fail("Kustomization base deve incluir outbox-alerting.yaml.", errors)
        if "outbox-dashboard.yaml" not in kustomization:
            fail("Kustomization base deve incluir outbox-dashboard.yaml.", errors)
        if "retention-alerting.yaml" not in kustomization:
            fail("Kustomization base deve incluir retention-alerting.yaml.", errors)
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
    if not OUTBOX_ALERTS.is_file():
        fail(f"Contrato de alertas da outbox ausente: {OUTBOX_ALERTS}", errors)
    else:
        outbox_alerts = json.loads(OUTBOX_ALERTS.read_text(encoding="utf-8"))
        if set(outbox_alerts.get("alerts", {})) != REQUIRED_OUTBOX_ALERTS:
            fail("Alertas da outbox devem cobrir stall, backlog, fila pronta, retry e idade.", errors)
        if outbox_alerts.get("notification_policy", {}).get("include_sensitive_payload") is not False:
            fail("Alertas da outbox nao podem incluir payload sensivel.", errors)
        if outbox_alerts.get("scope") != "outbox-dispatcher":
            fail("Alertas da outbox devem declarar scope outbox-dispatcher.", errors)
        if outbox_alerts.get("runbook") != "docs/OPERATIONS.md#outbox":
            fail("Alertas da outbox devem apontar para o runbook de operacao.", errors)
        for alert_name, alert in outbox_alerts.get("alerts", {}).items():
            if not alert.get("expr") or not alert.get("evidence") or "incident_ticket" not in alert.get("evidence", []):
                fail(f"Alerta da outbox incompleto: {alert_name}", errors)
        outbox_alerting = KUBERNETES_OUTBOX_ALERTING.read_text(encoding="utf-8") if KUBERNETES_OUTBOX_ALERTING.is_file() else ""
        if "kind: PrometheusRule" not in outbox_alerting or "kind: AlertmanagerConfig" not in outbox_alerting:
            fail("Alertas da outbox devem ter PrometheusRule e AlertmanagerConfig Kubernetes.", errors)
        for alert_name, alert in outbox_alerts.get("alerts", {}).items():
            if f"alert: {alert_name}" not in outbox_alerting or alert["expr"] not in outbox_alerting:
                fail(f"PrometheusRule da outbox nao materializa alerta: {alert_name}", errors)
    if not OUTBOX_DASHBOARD.is_file():
        fail(f"Contrato do dashboard da outbox ausente: {OUTBOX_DASHBOARD}", errors)
    else:
        outbox_dashboard = json.loads(OUTBOX_DASHBOARD.read_text(encoding="utf-8"))
        if outbox_dashboard.get("uid") != "outbox-dispatcher":
            fail("Dashboard da outbox deve declarar uid outbox-dispatcher.", errors)
        if outbox_dashboard.get("title") != "All-in-One - Outbox Dispatcher":
            fail("Dashboard da outbox deve declarar o titulo oficial.", errors)
        if set(outbox_dashboard.get("tags", [])) != {"all-in-one", "outbox", "operations"}:
            fail("Dashboard da outbox deve declarar as tags oficiais.", errors)
        if outbox_dashboard.get("refresh") != "30s":
            fail("Dashboard da outbox deve atualizar a cada 30s.", errors)
        panels = outbox_dashboard.get("panels", [])
        if len(panels) < 8:
            fail("Dashboard da outbox deve declarar ao menos 8 paineis.", errors)
        panel_titles = {panel.get("title") for panel in panels}
        if not REQUIRED_OUTBOX_DASHBOARD_TITLES.issubset(panel_titles):
            fail("Dashboard da outbox deve cobrir os paineis esperados.", errors)
        panel_exprs = {
            target.get("expr")
            for panel in panels
            for target in panel.get("targets", [])
            if isinstance(target, dict) and target.get("expr")
        }
        for metric in REQUIRED_OUTBOX_DASHBOARD_METRICS:
            if not any(metric in expr for expr in panel_exprs):
                fail(f"Dashboard da outbox nao referencia a metrica: {metric}", errors)
        outbox_dashboard_manifest = KUBERNETES_OUTBOX_DASHBOARD.read_text(encoding="utf-8") if KUBERNETES_OUTBOX_DASHBOARD.is_file() else ""
        if "kind: ConfigMap" not in outbox_dashboard_manifest or 'grafana_dashboard: "1"' not in outbox_dashboard_manifest:
            fail("Dashboard da outbox deve materializar ConfigMap Grafana.", errors)
        if "outbox-dispatcher-dashboard.json" not in outbox_dashboard_manifest:
            fail("Dashboard da outbox deve expor o JSON oficial no ConfigMap.", errors)
        if "All-in-One - Outbox Dispatcher" not in outbox_dashboard_manifest:
            fail("ConfigMap do dashboard da outbox deve conter o titulo oficial.", errors)
    if not DOMAIN_EVENT_FIXTURES.is_file():
        fail(f"Catalogo de fixtures de eventos ausente: {DOMAIN_EVENT_FIXTURES}", errors)
    else:
        event_fixtures = json.loads(DOMAIN_EVENT_FIXTURES.read_text(encoding="utf-8"))
        if event_fixtures.get("version") != "2026-06-30":
            fail("Catalogo de fixtures de eventos deve manter version=2026-06-30.", errors)
        if event_fixtures.get("source_catalog") != "config/module_catalog.json":
            fail("Catalogo de fixtures de eventos deve apontar para config/module_catalog.json.", errors)
        if event_fixtures.get("source_catalog_version") != CATALOG.get("version"):
            fail("Catalogo de fixtures de eventos deve referenciar a versao atual do catalogo.", errors)
        if event_fixtures.get("exchange") != "all-in-one.domain":
            fail("Catalogo de fixtures de eventos deve declarar o exchange all-in-one.domain.", errors)
        if event_fixtures.get("module_count") != len(modules):
            fail("Catalogo de fixtures de eventos deve cobrir um fixture por modulo.", errors)
        total_events = sum(len(module.get("events", [])) for module in modules)
        if event_fixtures.get("event_count") != total_events:
            fail("Catalogo de fixtures de eventos deve cobrir todos os eventos do catalogo.", errors)
        fixtures_modules = event_fixtures.get("modules", {})
        if set(fixtures_modules) != slugs:
            fail("Catalogo de fixtures de eventos deve cobrir exatamente os 25 modulos do catalogo.", errors)
        for module in modules:
            slug = module["slug"]
            expected_events = list(module.get("events", []))
            fixture_module = fixtures_modules.get(slug, {})
            if fixture_module.get("title") != module["title"]:
                fail(f"Catalogo de fixtures de eventos deve declarar o titulo oficial de {slug}.", errors)
            if fixture_module.get("routing_keys") != expected_events:
                fail(f"Catalogo de fixtures de eventos deve declarar routing keys de {slug} na mesma ordem do catalogo.", errors)
            fixture_events = fixture_module.get("events", [])
            if [event.get("routing_key") for event in fixture_events] != expected_events:
                fail(f"Catalogo de fixtures de eventos deve materializar as fixtures de {slug}.", errors)
            if len(fixture_events) != len(expected_events):
                fail(f"Catalogo de fixtures de eventos nao cobre todos os eventos de {slug}.", errors)
            for index, event in enumerate(fixture_events, start=1):
                expected_id = f"{slug}-fixture-{index:02d}"
                if event.get("schema_version") != 1:
                    fail(f"Fixture de evento invalida em {slug}: schema_version", errors)
                if event.get("occurred_at") != "2026-06-30T00:00:00Z":
                    fail(f"Fixture de evento invalida em {slug}: occurred_at", errors)
                expected_aggregate_type = str(event.get("routing_key", "")).rsplit(".", 1)[0]
                if event.get("aggregate_type") != expected_aggregate_type:
                    fail(f"Fixture de evento invalida em {slug}: aggregate_type", errors)
                if event.get("aggregate_id") != expected_id or event.get("entity_id") != expected_id:
                    fail(f"Fixture de evento invalida em {slug}: aggregate_id/entity_id", errors)
                if event.get("actor_user_id") != f"{slug}-fixture-actor":
                    fail(f"Fixture de evento invalida em {slug}: actor_user_id", errors)
                try:
                    uuid.UUID(str(event.get("event_id", "")))
                    uuid.UUID(str(event.get("correlation_id", "")))
                except (TypeError, ValueError):
                    fail(f"Fixture de evento invalida em {slug}: ids UUID", errors)
                payload = event.get("payload", {})
                expected_payload = {
                    "module": slug,
                    "routing_key": event.get("routing_key"),
                    "summary": f"Fixture de evento do modulo {module['title']}",
                }
                if payload != expected_payload:
                    fail(f"Fixture de evento invalida em {slug}: payload seguro", errors)

    if errors:
        print("\nFalhas de validacao encontradas:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nRepositorio validado com sucesso! Todos os 25 modulos e infraestrutura estao em conformidade.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
