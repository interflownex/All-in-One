from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_firebase_auth import validate as validate_firebase_auth
from scripts.validate_stitch_mcp_config import validate_stitch_mcp_config

CATALOG = json.loads(
    (ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8")
)
STITCH_MANIFEST = ROOT / "config" / "stitch" / "screen_manifest.json"
STITCH_MCP_POLICY = ROOT / "config" / "autonomy" / "stitch_mcp_policy.json"
MULTI_AGENT_SYNC_POLICY = ROOT / "config" / "autonomy" / "multi_agent_sync_policy.json"
GOOGLE_INTEGRATIONS_POLICY = (
    ROOT / "config" / "autonomy" / "google_integrations_policy.json"
)
DATA_AGENT_KIT_POLICY = ROOT / "config" / "autonomy" / "data_agent_kit_policy.json"
FIREBASE_AUTH_POLICY = ROOT / "config" / "autonomy" / "firebase_auth_policy.json"
CLOUDFLARE_WEB_POLICY = ROOT / "config" / "autonomy" / "cloudflare_web_policy.json"
TELEGRAM_DELIVERY_POLICY = (
    ROOT / "config" / "autonomy" / "telegram_delivery_policy.json"
)
GOOGLE_CLOUD_PROFILE = ROOT / "config" / "cloud" / "google_cloud_profile.json"
GOOGLE_CLOUD_INVENTORY = ROOT / "config" / "cloud" / "google_cloud_inventory.json"
APIGEE_API_HUB_PLAN = ROOT / "config" / "cloud" / "apigee_api_hub_plan.json"
MONGODB_CONTRACT = ROOT / "config" / "database" / "mongodb_contract.json"
STITCH_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "stitch-sync.yml"
BRAND_IDENTITY = ROOT / "config" / "branding" / "brand_identity.json"
COMPLIANCE_MATRIX = ROOT / "config" / "compliance" / "data_classification.json"
DATA_SUBJECT_RIGHTS = ROOT / "config" / "compliance" / "data_subject_rights.json"
RETENTION_JOBS = ROOT / "config" / "compliance" / "retention_jobs.json"
RETENTION_ALERTS = ROOT / "config" / "observability" / "retention_alerts.json"
SLO_CATALOG = ROOT / "config" / "observability" / "slo_catalog.json"
BACKUP_RESTORE_PLAN = ROOT / "config" / "operations" / "backup_restore_plan.json"
INCIDENT_RESPONSE_RUNBOOKS = (
    ROOT / "config" / "operations" / "incident_response_runbooks.json"
)
LOAD_TEST_PLAN = ROOT / "config" / "operations" / "load_test_plan.json"
SENSITIVE_PERMISSIONS_REVIEW = (
    ROOT / "config" / "security" / "sensitive_permissions_review.json"
)
PERMISSIONS_ENFORCEMENT_MATRIX = (
    ROOT / "config" / "security" / "permissions_enforcement_matrix.json"
)
PROVIDER_MATRIX = ROOT / "config" / "integrations" / "provider_matrix.json"
ENV_EXAMPLE = ROOT / ".env.example"
VSCODE_SETTINGS = ROOT / ".vscode" / "settings.json"
VSCODE_TASKS = ROOT / ".vscode" / "tasks.json"
DOCKER_COMPOSE = ROOT / "infra" / "docker" / "docker-compose.yml"
KUBERNETES_PLATFORM = ROOT / "infra" / "kubernetes" / "base" / "platform.yaml"
KUBERNETES_RETENTION_ALERTING = (
    ROOT / "infra" / "kubernetes" / "base" / "retention-alerting.yaml"
)
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
    "identity",
    "business",
    "permissions",
    "marketplace",
    "stock",
    "delivery",
    "services",
    "mobility",
    "erp",
    "wms",
    "tms",
    "crm",
    "bpm",
    "document",
    "finance",
    "billing",
    "fiscal",
    "hr",
    "health",
    "legal",
    "property",
    "audit",
    "compliance",
    "notifications",
    "api_hub",
    "insurance",
    "bi",
    "ai_core",
    "jobs",
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
    "DATA_AGENT_KIT_ENABLED",
    "GOOGLE_CLOUD_PROJECT",
    "PROJECT_ID",
    "GCP_REGION",
    "BIGQUERY_LOCATION",
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

APP_DIR_OVERRIDES = {
    "valley-business": "valley_business",
    "valley-rider": "valley_rider",
}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def resolve_app_dir(slug: str) -> Path:
    return ROOT / "apps" / APP_DIR_OVERRIDES.get(slug, slug)


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
        if not (resolve_app_dir(app["slug"]) / "README.md").is_file():
            fail(f"App ausente: {app['slug']}", errors)
    migrations = "
".join(
        item.read_text(encoding="utf-8")
        for item in sorted(
            (ROOT / "database" / "postgres" / "migrations").glob("*.sql")
        )
    )
    for schema in REQUIRED_SCHEMAS:
        if f"CREATE SCHEMA IF NOT EXISTS {schema}" not in migrations:
            fail(f"Schema PostgreSQL nao declarado: {schema}", errors)
    env_example = (
        ENV_EXAMPLE.read_text(encoding="utf-8") if ENV_EXAMPLE.is_file() else ""
    )
    if not env_example:
        fail("Contrato de variaveis ausente: .env.example", errors)
    for env_var in REQUIRED_ENV_VARS:
        if f"{env_var}=" not in env_example:
            fail(
                f"Variavel de ambiente obrigatoria nao declarada em .env.example: {env_var}",
                errors,
            )
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
    if not MONGODB_CONTRACT.is_file():
        fail(
            "Contrato MongoDB/NoSQL ausente: config/database/mongodb_contract.json",
            errors,
        )
    else:
        mongodb_contract = json.loads(MONGODB_CONTRACT.read_text(encoding="utf-8"))
        collections = mongodb_contract.get("collections", {})
        for collection in [
            "ai_memory",
            "social_videos",
            "influencer_metrics",
            "telemetry_logs",
        ]:
            if collection not in collections:
                fail(f"Contrato MongoDB deve declarar colecao {collection}.", errors)
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
    security_workflow = ROOT / ".github" / "workflows" / "security.yml"
    if security_workflow.is_file():
        security_text = security_workflow.read_text(encoding="utf-8")
        for command in [
            "pip-audit --local",
            "bandit -r modules/shared scripts workers -q -ll",
            "npm audit --omit=dev --audit-level=critical",
        ]:
            if command not in security_text:
                fail(
                    f"Workflow de seguranca deve manter scan obrigatorio: {command}",
                    errors,
                )
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
        if (
            "--import-mode=importlib" not in pytest_ini
            or "--basetemp=.pytest_tmp" not in pytest_ini
        ):
            fail(
                "pytest.ini deve centralizar importlib e basetemp local .pytest_tmp.",
                errors,
            )
    dockerignore_path = ROOT / ".dockerignore"
    if not dockerignore_path.is_file():
        fail(
            ".dockerignore ausente; builds Docker devem excluir caches, .venv e artefatos locais pesados.",
            errors,
        )
    else:
        dockerignore = dockerignore_path.read_text(encoding="utf-8")
        for ignored_path in [
            ".git",
            ".venv",
            ".pytest_cache",
            ".pytest_tmp",
            "node_modules",
            "tests",
            "apps",
        ]:
            if ignored_path not in dockerignore:
                fail(
                    f".dockerignore deve excluir {ignored_path} do contexto Docker.",
                    errors,
                )
    if not VSCODE_SETTINGS.is_file():
        fail("Configuracao VS Code ausente: .vscode/settings.json", errors)
    else:
        settings = json.loads(VSCODE_SETTINGS.read_text(encoding="utf-8"))
        expected_python = "${workspaceFolder}/.venv/bin/python"
        if settings.get("python.defaultInterpreterPath") != expected_python:
            fail(
                f"python.defaultInterpreterPath deve ser {expected_python}. Corrija no .vscode/settings.json e execute python -m venv .venv",
                errors,
            )
        if settings.get("python.testing.pytestArgs") not in ([], None):
            fail(
                "python.testing.pytestArgs deve ficar vazio; pytest.ini e a fonte obrigatoria.",
                errors,
            )
        if settings.get("mdb.presetConnections") not in ([], None):
            fail(
                "mdb.presetConnections deve ficar vazio para nao tentar conectar automaticamente ao Mongo local.",
                errors,
            )
        if (
            settings.get("geminicodeassist.outlines.automaticOutlineGeneration")
            is not True
        ):
            fail(
                "Gemini Code Assist deve permanecer ativo no Antigravity/editor.",
                errors,
            )
        if settings.get("geminicodeassist.enable") is not True:
            fail(
                "geminicodeassist.enable deve permanecer true no Antigravity/editor.",
                errors,
            )
        if settings.get("geminicodeassist.agentYoloMode") is not False:
            fail(
                "geminicodeassist.agentYoloMode deve permanecer false para evitar execucao destrutiva automatica.",
                errors,
            )
        invalid_kubeconfig = str(VSCODE_SETTINGS)
        if settings.get("cloudcode.active-kubeconfig") == invalid_kubeconfig:
            fail(
                "cloudcode.active-kubeconfig nao pode apontar para .vscode/settings.json; use kubeconfig real fora do workspace.",
                errors,
            )
        for kubeconfig in settings.get("cloudcode.kubeconfigs") or []:
            if kubeconfig.get("configPath") == invalid_kubeconfig:
                fail(
                    "cloudcode.kubeconfigs nao pode registrar .vscode/settings.json como kubeconfig.",
                    errors,
                )
        expected_cloudcode = {
            "google.cloud.project": "all-in-one-498012",
            "cloudcode.autoDependencies": "on",
            "cloudcode.active-kubeconfig": "all-in-one-local",
            "cloudcode.enableTelemetry": False,
            "cloudcode.enableCrashReporting": False,
            "cloudcode.useGcloudAuthSkaffold": True,
            "cloudcode.enableGkeAutopilotSupport": True,
        }
        for setting_name, expected_value in expected_cloudcode.items():
            if settings.get(setting_name) != expected_value:
                fail(f"Configuracao Cloud Code invalida: {setting_name}.", errors)
        expected_kubernetes = {
            "vscode-kubernetes.kubectl-path": "/usr/local/bin/kubectl",
            "vscode-kubernetes.helm-path": "/usr/local/bin/helm",
            "vs-kubernetes.kubeconfig": "/home/eretazan/.kube/config",
            "vs-kubernetes.kubectlVersioning": "user-provided",
            "vs-kubernetes.outputFormat": "yaml",
            "imageBuildTool": "Docker",
        }
        for setting_name, expected_value in expected_kubernetes.items():
            if settings.get(setting_name) != expected_value:
                fail(f"Configuracao Kubernetes invalida: {setting_name}.", errors)
    vscode_extens