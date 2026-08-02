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
WSL_DNS_POLICY = ROOT / "config" / "autonomy" / "wsl_dns_policy.json"
SSH_REMOTE_ACCESS_POLICY = (
    ROOT / "config" / "autonomy" / "ssh_remote_access_policy.json"
)
ANTIGRAVITY_TRUST_POLICY = (
    ROOT / "config" / "autonomy" / "antigravity_trust_policy.json"
)
TELEGRAM_DELIVERY_POLICY = (
    ROOT / "config" / "autonomy" / "telegram_delivery_policy.json"
)
GOOGLE_CLOUD_PROFILE = ROOT / "config" / "cloud" / "google_cloud_profile.json"
GOOGLE_CLOUD_INVENTORY = ROOT / "config" / "cloud" / "google_cloud_inventory.json"
APIGEE_API_HUB_PLAN = ROOT / "config" / "cloud" / "apigee_api_hub_plan.json"
MONGODB_CONTRACT = ROOT / "config" / "database" / "mongodb_contract.json"
STITCH_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "stitch-sync.yml"
DEPLOY_GKE_WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"
CLOUDFLARE_PAGES_WORKFLOW = ROOT / ".github" / "workflows" / "cloudflare-pages.yml"
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
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_PAGES_PROJECT_NAME",
    "CLOUDFLARE_PAGES_DOMAIN",
    "CLOUDFLARE_TUNNEL_NAME",
    "CLOUDFLARE_TUNNEL_TOKEN",
    "CLOUDFLARE_TUNNEL_API_HOSTNAME",
    "CLOUDFLARE_TUNNEL_API_ORIGIN",
    "CLOUDFLARE_TUNNEL_STREAM_HOSTNAME",
    "CLOUDFLARE_TUNNEL_STREAM_ORIGIN",
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
    if len(slugs) != 24 or "vision" in slugs:
        fail(
            "Catalogo deve declarar exatamente os 24 modulos ativos e manter Vision inativo.",
            errors,
        )
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
    migrations = "\n".join(
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
            "pip-audit -r requirements-dev.txt",
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
        for setting_name in settings:
            if setting_name.startswith(("google.cloud.", "google.datacloud.", "cloudcode.")):
                fail(
                    f"Configuracao Google Cloud paga deve ficar ausente no modo local-first: {setting_name}.",
                    errors,
                )
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
        for env_scope in [
            "terminal.integrated.env.windows",
            "terminal.integrated.env.linux",
        ]:
            terminal_env = settings.get(env_scope, {})
            expected_local_first = {
                "GOOGLE_INTEGRATIONS_ENABLED": "false",
                "GOOGLE_CLOUD_ENABLED": "false",
                "GOOGLE_AI_STUDIO_ENABLED": "false",
                "GOOGLE_CODE_CLI_ENABLED": "false",
                "ALLOYDB_ENABLED": "false",
                "STITCH_REMOTE_SYNC_ENABLED": "false",
                "DATA_AGENT_KIT_ENABLED": "false",
                "GEMINI_CODE_ASSIST_ENABLED": "true",
            }
            for env_name, expected_value in expected_local_first.items():
                if terminal_env.get(env_name) != expected_value:
                    fail(
                        f"{env_scope}.{env_name} deve permanecer {expected_value} no modo local-first.",
                        errors,
                    )
    vscode_extensions = ROOT / ".vscode" / "extensions.json"
    if not vscode_extensions.is_file():
        fail("Configuracao VS Code ausente: .vscode/extensions.json", errors)
    else:
        extensions = json.loads(vscode_extensions.read_text(encoding="utf-8"))
        recommendations = set(extensions.get("recommendations", []))
        for extension in [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            "ms-kubernetes-tools.vscode-kubernetes-tools",
        ]:
            if extension not in recommendations:
                fail(
                    f"Extensao VS Code Python obrigatoria ausente em .vscode/extensions.json: {extension}",
                    errors,
                )
        for extension in ["googlecloudtools.cloudcode", "GoogleCloudTools.datacloud"]:
            if extension in recommendations:
                fail(
                    f"Extensao Google Cloud paga nao deve ser recomendada no modo local-first: {extension}",
                    errors,
                )
    if not VSCODE_TASKS.is_file():
        fail("Configuracao VS Code ausente: .vscode/tasks.json", errors)
    else:
        tasks = json.loads(VSCODE_TASKS.read_text(encoding="utf-8"))
        pytest_tasks = [
            task
            for task in tasks.get("tasks", [])
            if task.get("label") == "test: pytest completo"
        ]
        if not pytest_tasks:
            fail("Task VS Code test: pytest completo ausente.", errors)
        elif (
            pytest_tasks[0].get("command") != "${config:python.defaultInterpreterPath}"
        ):
            fail(
                "Task pytest deve usar ${config:python.defaultInterpreterPath}.", errors
            )
    if not (ROOT / "workers" / "outbox_dispatcher" / "main.py").is_file():
        fail("Worker da outbox RabbitMQ ausente.", errors)
    for relative in [
        "workers/retention_worker/main.py",
        "modules/shared/retention_worker.py",
    ]:
        if not (ROOT / relative).is_file():
            fail(f"Worker de retencao LGPD ausente: {relative}", errors)
    compose = (
        DOCKER_COMPOSE.read_text(encoding="utf-8") if DOCKER_COMPOSE.is_file() else ""
    )
    if (
        "retention-worker:" not in compose
        or "workers/retention_worker/Dockerfile" not in compose
    ):
        fail("Docker Compose deve agendar o worker de retencao LGPD.", errors)
    if "deletion_worker_daily --dry-run" not in compose:
        fail(
            "Docker Compose deve manter descarte LGPD em dry-run ate homologacao por modulo.",
            errors,
        )
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
            fail(
                f"Docker Compose deve manter o contrato local-first com coordenada futura Google: {active_env}",
                errors,
            )
    if not WSL_DNS_POLICY.is_file():
        fail("Politica obrigatoria de DNS WSL ausente.", errors)
    else:
        wsl_dns_policy = json.loads(WSL_DNS_POLICY.read_text(encoding="utf-8"))
        resolved = wsl_dns_policy.get("resolved", {})
        validation = wsl_dns_policy.get("validation", {})
        if wsl_dns_policy.get("wsl", {}).get("disable_generated_resolv_conf") is not True:
            fail("DNS WSL deve desativar generateResolvConf.", errors)
        if resolved.get("resolv_conf_symlink_target") != "/run/systemd/resolve/stub-resolv.conf":
            fail("DNS WSL deve manter /etc/resolv.conf no stub systemd-resolved.", errors)
        if resolved.get("stub_nameserver") != "127.0.0.53":
            fail("DNS WSL deve expor o stub 127.0.0.53.", errors)
        if "10.255.255.254" not in resolved.get("dns", []):
            fail("DNS WSL deve preservar o resolvedor do gateway WSL.", errors)
        if "1.1.1.1" not in resolved.get("fallback_dns", []) and "1.1.1.1" not in resolved.get("dns", []):
            fail("DNS WSL deve manter fallback publico Cloudflare.", errors)
        if validation.get("command") != "python3 scripts/configure_wsl_dns.py --check":
            fail("DNS WSL deve declarar o comando de validacao versionado.", errors)
        if not (ROOT / "scripts" / "configure_wsl_dns.py").is_file():
            fail("Script de DNS WSL ausente: scripts/configure_wsl_dns.py", errors)
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
        fail(
            "Contrato de branding oficial ausente: config/branding/brand_identity.json",
            errors,
        )
    else:
        brand = json.loads(BRAND_IDENTITY.read_text(encoding="utf-8"))
        for relative in [
            brand.get("platform_brand", {}).get("logo_asset"),
            brand.get("valley_brand", {}).get("logo_asset"),
        ]:
            if not relative or not (ROOT / relative).is_file():
                fail(f"Ativo oficial de marca ausente: {relative}", errors)
        if set(brand.get("valley_apps", [])) != {"valley", "valley-business"}:
            fail("Branding deve declarar exatamente os apps Valley oficiais.", errors)
        if set(brand.get("riders_apps", [])) != {
            "valley-rider",
            "all-in-one-riders",
        }:
            fail("Branding deve declarar exatamente os apps Riders oficiais.", errors)
    if not STITCH_MCP_POLICY.is_file():
        fail("Politica obrigatoria do MCP Stitch ausente.", errors)
    else:
        for error in validate_stitch_mcp_config(
            require_secret=False, require_codex_config=False
        ):
            fail(error, errors)
        stitch_policy = json.loads(STITCH_MCP_POLICY.read_text(encoding="utf-8"))
        if stitch_policy.get("enabled") is not True:
            fail("Politica Stitch deve permanecer enabled=true.", errors)
        if stitch_policy.get("reactivated_at") != "2026-06-06":
            fail("Politica Stitch deve registrar a reativacao de 2026-06-06.", errors)
    if not GOOGLE_INTEGRATIONS_POLICY.is_file():
        fail("Politica obrigatoria de integracoes Google ausente.", errors)
    else:
        google_policy = json.loads(
            GOOGLE_INTEGRATIONS_POLICY.read_text(encoding="utf-8")
        )
        if google_policy.get("enabled") is not True:
            fail("Politica Google deve permanecer enabled=true.", errors)
        if google_policy.get("reactivated_at") != "2026-07-30T05:00:00-03:00":
            fail("Politica Google deve registrar a reativacao de 2026-07-30.", errors)
        expected_integrations = {
            "google_sdk",
            "google_ai_studio",
            "google_cloud",
            "alloydb",
            "google_code_cli",
            "gemini_cli_termux",
            "gemini_cli_ubuntu",
            "google_stitch_mcp",
            "google_cloud_data_agent_kit",
        }
        if set(google_policy.get("affected_integrations", [])) != expected_integrations:
            fail(
                "Politica Google deve cobrir SDK, AI Studio, Cloud, AlloyDB, Code CLI e Gemini CLI.",
                errors,
            )
        runtime = google_policy.get("runtime_environment", {})
        expected_runtime = {
            "GOOGLE_INTEGRATIONS_ENABLED": "false",
            "GOOGLE_CLOUD_ENABLED": "false",
            "GOOGLE_AI_STUDIO_ENABLED": "false",
            "GOOGLE_CODE_CLI_ENABLED": "false",
            "ALLOYDB_ENABLED": "false",
            "GEMINI_CODE_ASSIST_ENABLED": "true",
            "STITCH_REMOTE_SYNC_ENABLED": "false",
            "STITCH_COORDINATOR": "codex",
            "STITCH_LEGACY_MODULE_SYNC_ENABLED": "false",
            "DATA_AGENT_KIT_ENABLED": "false",
        }
        for variable, expected_value in expected_runtime.items():
            if runtime.get(variable) != expected_value:
                fail(
                    f"Politica Google deve manter {variable}={expected_value}.",
                    errors,
                )
        if set(google_policy.get("explicit_exceptions", [])) != {
            "google_stitch_mcp",
            "gemini_code_assist",
        }:
            fail(
                "Politica Google deve manter somente Stitch MCP e Gemini Code Assist como excecoes ativas.",
                errors,
            )
    if not DATA_AGENT_KIT_POLICY.is_file():
        fail("Politica obrigatoria do Google Cloud Data Agent Kit ausente.", errors)
    else:
        data_agent_policy = json.loads(
            DATA_AGENT_KIT_POLICY.read_text(encoding="utf-8")
        )
        starter_pack = data_agent_policy.get("starter_pack", {})
        defaults = data_agent_policy.get("defaults", {})
        security = data_agent_policy.get("security", {})
        if (
            data_agent_policy.get("enabled") is not False
            or starter_pack.get("version") != "0.6.1"
        ):
            fail(
                "Data Agent Kit deve permanecer suspenso na versao homologada 0.6.1.",
                errors,
            )
        if (
            defaults.get("project_id") != "all-in-one-498012"
            or defaults.get("region") != "southamerica-east1"
        ):
            fail("Data Agent Kit deve usar o projeto e a regiao autoritativos.", errors)
        if (
            security.get("credentials_outside_git") is not True
            or security.get("allow_destructive_data_operations") is not False
        ):
            fail(
                "Data Agent Kit deve preservar credenciais fora do Git e bloquear operacoes destrutivas.",
                errors,
            )
    deploy_gke_workflow = (
        DEPLOY_GKE_WORKFLOW.read_text(encoding="utf-8")
        if DEPLOY_GKE_WORKFLOW.is_file()
        else ""
    )
    if not deploy_gke_workflow:
        fail("Workflow GKE ausente: .github/workflows/deploy.yml", errors)
    else:
        for forbidden in ["  push:", "branches: [main]"]:
            if forbidden in deploy_gke_workflow:
                fail(
                    f"Workflow GKE nao deve disparar automaticamente no modo local-first: {forbidden}",
                    errors,
                )
        for needle in [
            "workflow_dispatch:",
            "confirm_gcp_billing_enabled",
            'GOOGLE_CLOUD_ENABLED: "false"',
            'GOOGLE_CLOUD_ENABLED: "true"',
            "inputs.confirm_gcp_billing_enabled == true",
            "inputs.confirm_gcp_billing_enabled != true",
            "gcloud container clusters get-credentials",
        ]:
            if needle not in deploy_gke_workflow:
                fail(
                    f"Workflow GKE deve permanecer manual e protegido por billing legitimo: {needle}",
                    errors,
                )
    if not FIREBASE_AUTH_POLICY.is_file():
        fail("Politica obrigatoria do Firebase Auth ausente.", errors)
    else:
        for error in validate_firebase_auth():
            fail(error, errors)
    if not CLOUDFLARE_WEB_POLICY.is_file():
        fail("Politica obrigatoria do ambiente web Cloudflare ausente.", errors)
    else:
        cloudflare_policy = json.loads(
            CLOUDFLARE_WEB_POLICY.read_text(encoding="utf-8")
        )
        if cloudflare_policy.get("provider") != "cloudflare_pages":
            fail("Ambiente web deve usar Cloudflare Pages.", errors)
        if cloudflare_policy.get("project_name") != "all-in-one-web":
            fail("Projeto Cloudflare Pages deve ser all-in-one-web.", errors)
        if (
            cloudflare_policy.get("spa_fallback")
            != "cloudflare_pages_automatic_without_404"
        ):
            fail(
                "Cloudflare Pages deve declarar o fallback SPA automatico sem 404.html.",
                errors,
            )
        if cloudflare_policy.get("wrangler_config") != "apps/all-in-one/wrangler.jsonc":
            fail("Cloudflare Pages deve declarar o wrangler.jsonc versionado.", errors)
        if cloudflare_policy.get("workspace_profile") != "config/cloudflare/workspace_profile.json":
            fail("Cloudflare deve declarar o perfil WSL versionado.", errors)
        cloudflare_profile_path = ROOT / "config" / "cloudflare" / "workspace_profile.json"
        if not cloudflare_profile_path.is_file():
            fail("Perfil Cloudflare WSL ausente.", errors)
        else:
            cloudflare_profile = json.loads(cloudflare_profile_path.read_text(encoding="utf-8"))
            if cloudflare_profile.get("tunnel", {}).get("token_env_var") != "CLOUDFLARE_TUNNEL_TOKEN":
                fail("Cloudflare Tunnel deve depender de CLOUDFLARE_TUNNEL_TOKEN fora do Git.", errors)
            if cloudflare_profile.get("tunnel", {}).get("no_inbound_ports_required") is not True:
                fail("Cloudflare Tunnel deve manter origem sem portas inbound publicas.", errors)
            stream_hostnames = [
                hostname
                for hostname in cloudflare_profile.get("tunnel", {}).get("desired_public_hostnames", [])
                if hostname.get("hostname") == "stream.brasildesconto.com.br"
            ]
            if stream_hostnames != [
                {
                    "hostname": "stream.brasildesconto.com.br",
                    "origin": "http://127.0.0.1:8100",
                    "purpose": "api_hub_stream_path",
                }
            ]:
                fail("Cloudflare Tunnel stream deve apontar apenas para API Hub em 8100.", errors)
            if cloudflare_profile.get("mcp", {}).get("api", {}).get("bearer_token_env_var") != "CLOUDFLARE_API_TOKEN":
                fail("Cloudflare MCP API deve usar CLOUDFLARE_API_TOKEN por variavel de ambiente.", errors)
        if (
            cloudflare_policy.get("security_headers")
            != "apps/all-in-one/public/_headers"
        ):
            fail(
                "Cloudflare Pages deve declarar headers de seguranca versionados.",
                errors,
            )
        if set(cloudflare_policy.get("required_secrets", [])) != {
            "CLOUDFLARE_API_TOKEN",
            "CLOUDFLARE_ACCOUNT_ID",
        }:
            fail(
                "Politica Cloudflare deve exigir token e account ID fora do Git.",
                errors,
            )
        cloudflare_pages_workflow = (
            CLOUDFLARE_PAGES_WORKFLOW.read_text(encoding="utf-8")
            if CLOUDFLARE_PAGES_WORKFLOW.is_file()
            else ""
        )
        if not cloudflare_pages_workflow:
            fail("Workflow Cloudflare Pages ausente.", errors)
        else:
            for forbidden in ['wranglerVersion: "4.112.0"']:
                if forbidden in cloudflare_pages_workflow:
                    fail(f"Workflow Cloudflare Pages usa Wrangler obsoleto: {forbidden}", errors)
            for needle in [
                'WRANGLER_VERSION: "4.118.0"',
                "HAS_CLOUDFLARE_API_TOKEN",
                "HAS_CLOUDFLARE_ACCOUNT_ID",
                "deploy_enabled=true",
                "deploy_enabled=false",
                "if: steps.credentials.outputs.deploy_enabled == 'true'",
                "wranglerVersion: ${{ env.WRANGLER_VERSION }}",
                "HAS_TELEGRAM_DELIVERY",
            ]:
                if needle not in cloudflare_pages_workflow:
                    fail(
                        f"Workflow Cloudflare Pages deve ser idempotente e protegido por secrets: {needle}",
                        errors,
                    )
    if not SSH_REMOTE_ACCESS_POLICY.is_file():
        fail("Politica obrigatoria de acesso SSH remoto ausente.", errors)
    else:
        ssh_policy = json.loads(SSH_REMOTE_ACCESS_POLICY.read_text(encoding="utf-8"))
        server = ssh_policy.get("server", {})
        client_key = ssh_policy.get("client_key", {})
        tailscale = ssh_policy.get("tailscale", {})
        cloudflare_ssh = ssh_policy.get("cloudflare", {})
        manual = ssh_policy.get("manual", {})
        if ssh_policy.get("enabled") is not True:
            fail("Politica SSH deve permanecer enabled=true.", errors)
        if ssh_policy.get("access_channel") != "tailscale_only":
            fail("Acesso SSH remoto deve permanecer restrito ao Tailscale.", errors)
        if (
            server.get("password_authentication") is not False
            or server.get("keyboard_interactive_authentication") is not False
            or server.get("permit_root_login") is not False
            or server.get("authentication_methods") != ["publickey"]
        ):
            fail("Politica SSH deve exigir somente chave publica e bloquear senha/root.", errors)
        if client_key.get("storage") != "outside_git" or not str(
            client_key.get("private_key_path", "")
        ).startswith("/home/eretazan/.ssh/"):
            fail("Chave privada SSH deve permanecer fora do Git em ~/.ssh.", errors)
        if manual.get("storage") != "outside_git" or not str(
            manual.get("pdf_path", "")
        ).startswith("/home/eretazan/.local/share/all-in-one/secure/"):
            fail("Manual SSH sensivel deve permanecer fora do Git.", errors)
        if tailscale.get("required") is not True or tailscale.get("accept_dns") is not True:
            fail("Politica SSH deve exigir Tailscale com accept-dns ativo.", errors)
        if cloudflare_ssh.get("publish_ssh") is not False:
            fail("Cloudflare Tunnel nao pode publicar SSH.", errors)
        if "ssh" not in set(cloudflare_ssh.get("tunnel_must_not_expose", [])):
            fail("Politica SSH deve bloquear exposicao SSH em tunnel Cloudflare.", errors)
    if not TELEGRAM_DELIVERY_POLICY.is_file():
        fail("Politica obrigatoria de entrega via Telegram ausente.", errors)
    else:
        telegram_policy = json.loads(
            TELEGRAM_DELIVERY_POLICY.read_text(encoding="utf-8")
        )
        targets = telegram_policy.get("targets", {})
        if (
            telegram_policy.get("enabled") is not True
            or telegram_policy.get("channel") != "telegram"
        ):
            fail(
                "Entrega de artefatos prontos via Telegram deve permanecer ativa.",
                errors,
            )
        if set(telegram_policy.get("required_secrets", [])) != {
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
        }:
            fail("Politica Telegram deve exigir token e chat ID fora do Git.", errors)
        if telegram_policy.get("credentials_outside_git") is not True:
            fail("Credenciais do Telegram devem permanecer fora do Git.", errors)
        if set(targets) != {"web", "app"}:
            fail("Politica Telegram deve cobrir ambiente web e aplicativo.", errors)
        if targets.get("web", {}).get("delivery") != "public_url_and_version":
            fail("Entrega web via Telegram deve incluir URL publica e versao.", errors)
        if (
            targets.get("web", {}).get("identity_marker")
            != "<title>All-in-One — Ecossistema Digital</title>"
        ):
            fail(
                "Entrega web via Telegram deve validar a identidade exata do ambiente.",
                errors,
            )
        if targets.get("app", {}).get("delivery") != "installable_artifact_and_version":
            fail(
                "Entrega do aplicativo via Telegram deve incluir artefato instalavel e versao.",
                errors,
            )
    if not GOOGLE_CLOUD_PROFILE.is_file():
        fail(
            "Perfil Google Cloud ativo ausente: config/cloud/google_cloud_profile.json",
            errors,
        )
    else:
        cloud_profile = json.loads(GOOGLE_CLOUD_PROFILE.read_text(encoding="utf-8"))
        if cloud_profile.get("enabled") is not True:
            fail("Perfil Google Cloud deve permanecer enabled=true.", errors)
        required_apis = set(cloud_profile.get("required_apis", []))
        for required_api in {
            "aiplatform.googleapis.com",
            "alloydb.googleapis.com",
            "apigee.googleapis.com",
            "apihub.googleapis.com",
            "cloudkms.googleapis.com",
            "run.googleapis.com",
        }:
            if required_api not in required_apis:
                fail(f"Perfil Google Cloud deve habilitar {required_api}.", errors)
        safety = cloud_profile.get("safety", {})
        for forbidden in [
            "allow_delete",
            "allow_billing_change",
            "allow_policy_bypass",
        ]:
            if safety.get(forbidden) is not False:
                fail(f"Perfil Google Cloud deve manter {forbidden}=false.", errors)
        if cloud_profile.get("authoritative_project") != "all-in-one-498012":
            fail(
                "Perfil Google Cloud deve apontar para o projeto autoritativo all-in-one-498012.",
                errors,
            )
        if cloud_profile.get("authority_mode") != "remote_state_is_authoritative":
            fail(
                "Perfil Google Cloud deve tratar o estado remoto como autoritativo.",
                errors,
            )
        if safety.get("requires_import_before_change") is not True:
            fail(
                "Perfil Google Cloud deve exigir importacao antes de mudancas.", errors
            )
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
        if any(
            security.get(flag) is not False
            for flag in [
                "secrets_included",
                "api_key_values_included",
                "service_account_private_keys_included",
                "kms_key_material_included",
            ]
        ):
            fail(
                "Inventario Google Cloud nao pode incluir segredos ou material criptografico.",
                errors,
            )
    if not APIGEE_API_HUB_PLAN.is_file():
        fail(
            "Plano Apigee API Hub ausente: config/cloud/apigee_api_hub_plan.json",
            errors,
        )
    else:
        api_hub_plan = json.loads(APIGEE_API_HUB_PLAN.read_text(encoding="utf-8"))
        host_project = api_hub_plan.get("host_project", {})
        encryption = api_hub_plan.get("encryption", {})
        service_identity = api_hub_plan.get("service_identity", {})
        safety = api_hub_plan.get("safety", {})
        if api_hub_plan.get("authority_mode") != "remote_state_is_authoritative":
            fail(
                "Plano Apigee API Hub deve respeitar estado remoto autoritativo.",
                errors,
            )
        if (
            host_project.get("project_id") != "all-in-one-498012"
            or host_project.get("project_number") != "864981916504"
        ):
            fail(
                "Plano Apigee API Hub deve apontar para o projeto host all-in-one-498012/864981916504.",
                errors,
            )
        if (
            api_hub_plan.get("location", {}).get("api_hub_location")
            != "southamerica-west1"
        ):
            fail(
                "Plano Apigee API Hub deve preservar a location southamerica-west1 do inventario.",
                errors,
            )
        if encryption.get("mode") != "customer_managed_encryption_key":
            fail("Plano Apigee API Hub deve declarar CMEK para criptografia.", errors)
        hmac = api_hub_plan.get("cloud_storage_hmac", {})
        if (
            hmac.get("service_account")
            != "service-account@all-in-one-498012.iam.gserviceaccount.com"
        ):
            fail(
                "Plano Apigee deve registrar a conta de servico HMAC solicitada.",
                errors,
            )
        if hmac.get("secret_material_in_git") is not False:
            fail("Plano Apigee deve impedir segredo HMAC no Git.", errors)
        kms_key = encryption.get("kms_key_resource")
        if not kms_key:
            fail("Plano Apigee API Hub deve declarar a chave KMS selecionada.", errors)
        if kms_key not in set(encryption.get("allowed_inventory_keys", [])):
            fail(
                "Plano Apigee API Hub deve usar uma chave KMS permitida pelo inventario.",
                errors,
            )
        if encryption.get("secret_material_in_git") is not False:
            fail("Plano Apigee API Hub deve proibir material KMS no Git.", errors)
        if (
            service_identity.get("email")
            != "service-864981916504@gcp-sa-apihub.iam.gserviceaccount.com"
        ):
            fail(
                "Plano Apigee API Hub deve registrar a service identity informada.",
                errors,
            )
        expected_roles = {
            "roles/cloudkms.cryptoKeyEncrypterDecrypter",
            "roles/apihub.admin",
            "roles/apihub.runtimeProjectServiceAgent",
        }
        if {
            grant.get("role") for grant in api_hub_plan.get("iam_grants", [])
        } != expected_roles:
            fail(
                "Plano Apigee API Hub deve declarar exatamente os roles IAM esperados.",
                errors,
            )
        for forbidden in [
            "allow_delete",
            "allow_billing_change",
            "allow_policy_bypass",
        ]:
            if safety.get(forbidden) is not False:
                fail(f"Plano Apigee API Hub deve manter {forbidden}=false.", errors)
    if not PROVIDER_MATRIX.is_file():
        fail(
            "Matriz de provedores ausente: config/integrations/provider_matrix.json",
            errors,
        )
    else:
        provider_matrix = json.loads(PROVIDER_MATRIX.read_text(encoding="utf-8"))
        integrations = {
            item.get("key"): item for item in provider_matrix.get("integrations", [])
        }
        maps = integrations.get("maps_routing_tracking", {})
        active_maps = set(maps.get("primary_candidates", [])) | set(
            maps.get("fallback_candidates", [])
        )
        if "Google Maps Platform" not in active_maps:
            fail(
                "Google Maps Platform deve permanecer entre os candidatos ativos.",
                errors,
            )
        ai_agent = integrations.get("ai_agent_superdesign", {})
        if not str(ai_agent.get("primary_model", "")).lower().startswith("google/"):
            fail(
                "Modelo primario do agente AI deve usar Google/Gemini apos a reativacao.",
                errors,
            )
        active_ai = set(ai_agent.get("primary_candidates", [])) | set(
            ai_agent.get("fallback_candidates", [])
        )
        if "Google Gemini API" not in active_ai:
            fail(
                "Google Gemini API deve permanecer entre os candidatos ativos.", errors
            )
    if not MULTI_AGENT_SYNC_POLICY.is_file():
        fail("Politica obrigatoria de alinhamento multiagente ausente.", errors)
    else:
        multi_agent_policy = json.loads(
            MULTI_AGENT_SYNC_POLICY.read_text(encoding="utf-8")
        )
        if multi_agent_policy.get("enabled") is not True:
            fail("Politica multiagente deve estar habilitada.", errors)
        if multi_agent_policy.get("language") != "pt-BR":
            fail("Politica multiagente deve manter idioma pt-BR.", errors)
        source_of_truth = multi_agent_policy.get("source_of_truth", {})
        if (
            source_of_truth.get("repository") != "git"
            or source_of_truth.get("preferred_push_remote") != "fork"
        ):
            fail(
                "Politica multiagente deve declarar Git e remoto fork como contrato de sincronizacao.",
                errors,
            )
        agent_ids = {agent.get("id") for agent in multi_agent_policy.get("agents", [])}
        if agent_ids != REQUIRED_MULTI_AGENT_IDS:
            fail(
                "Politica multiagente deve cobrir Codex CLI, Antigravity, Gemini Code e Gemini CLI Termux/Ubuntu.",
                errors,
            )
        enabled_agents = {
            agent.get("id")
            for agent in multi_agent_policy.get("agents", [])
            if agent.get("enabled") is True
        }
        if not {"gemini_code", "gemini_cli_termux", "gemini_cli_ubuntu"}.issubset(
            enabled_agents
        ):
            fail(
                "Gemini Code Assist e Gemini CLI Termux/Ubuntu devem permanecer ativos.",
                errors,
            )
        mandatory_rules = "\n".join(multi_agent_policy.get("mandatory_rules", []))
        for needle in REQUIRED_MULTI_AGENT_RULES:
            if needle not in mandatory_rules:
                fail(f"Politica multiagente incompleta: {needle}", errors)
        stitch_alignment = multi_agent_policy.get("stitch_alignment", {})
        if (
            stitch_alignment.get("state") != "config/stitch/sync_state.json"
            or stitch_alignment.get("remote_secret") != "STITCH_API_KEY"
        ):
            fail(
                "Politica multiagente deve preservar estado Stitch e segredo remoto oficial.",
                errors,
            )
        if stitch_alignment.get("enabled") is not True:
            fail(
                "Alinhamento Stitch remoto deve permanecer ativo na politica multiagente.",
                errors,
            )
        coordination_guard = multi_agent_policy.get("coordination_guard", {})
        if coordination_guard.get("script") != "scripts/multi_agent_sync_guard.py":
            fail(
                "Politica multiagente deve apontar para o guardiao de coordenacao versionado.",
                errors,
            )
        if coordination_guard.get("required_before_edit") is not True:
            fail("Guardiao multiagente deve ser obrigatorio antes de editar.", errors)
        pre_work_commands = "\n".join(multi_agent_policy.get("pre_work_commands", []))
        if "multi_agent_sync_guard.py preflight --integrate" not in pre_work_commands:
            fail(
                "Politica multiagente deve executar preflight remoto antes da edicao.",
                errors,
            )
        if "multi_agent_sync_guard.py acquire" not in pre_work_commands:
            fail("Politica multiagente deve adquirir lock antes da edicao.", errors)
    for agent_contract in ["AGENTS.md", "GEMINI.md"]:
        contract_text = (
            (ROOT / agent_contract).read_text(encoding="utf-8")
            if (ROOT / agent_contract).is_file()
            else ""
        )
        if "config/autonomy/multi_agent_sync_policy.json" not in contract_text:
            fail(
                f"{agent_contract} deve referenciar a politica multiagente obrigatoria.",
                errors,
            )
    antigravity_config = ROOT / ".agents" / "antigravity.json"
    if not ANTIGRAVITY_TRUST_POLICY.is_file():
        fail("Politica Antigravity trust ausente.", errors)
    else:
        antigravity_policy = json.loads(
            ANTIGRAVITY_TRUST_POLICY.read_text(encoding="utf-8")
        )
        if antigravity_policy.get("docker_mcp", {}).get("profile") != "all_in_one_local":
            fail("Antigravity deve usar o perfil Docker MCP all_in_one_local.", errors)
        trusted_wsl = antigravity_policy.get("trusted_workspaces", {}).get("wsl", "")
        if not trusted_wsl.startswith("/home/") or not trusted_wsl.endswith("/all-in-one"):
            fail("Antigravity deve confiar no workspace WSL All-in-One.", errors)
        if "cloudflare-api" not in antigravity_policy.get("essential_mcp_servers", []):
            fail("Antigravity deve manter Cloudflare MCP API essencial.", errors)
        if "datacloud_bigquery_remote" not in antigravity_policy.get("disabled_mcp_servers", []):
            fail("Antigravity deve desativar DataCloud BigQuery no modo local-first.", errors)
    if not antigravity_config.is_file():
        fail("Contrato Antigravity ausente: .agents/antigravity.json", errors)
    else:
        antigravity = json.loads(antigravity_config.read_text(encoding="utf-8"))
        if antigravity.get("name") != "antigravity":
            fail("Contrato Antigravity deve declarar name=antigravity.", errors)
        required_mcp_servers = {
            "filesystem-all-in-one",
            "context7",
            "cloudflare-docs",
            "cloudflare-api",
            "docker",
            "stitch",
        }
        if not required_mcp_servers.issubset(set(antigravity.get("mcp_servers", []))):
            fail(
                "Contrato Antigravity deve manter somente os MCPs essenciais "
                "do projeto ativos.",
                errors,
            )
        redundant_mcp_servers = {
            "cloudrun",
            "figma",
            "gke-oss",
            "github-official",
            "linear",
            "playwright",
            "terraform",
        }
        if redundant_mcp_servers.intersection(set(antigravity.get("mcp_servers", []))):
            fail(
                "Contrato Antigravity nao deve duplicar MCPs opcionais ou "
                "fornecidos pelo Docker Gateway.",
                errors,
            )
    stitch_workflow = (
        STITCH_SYNC_WORKFLOW.read_text(encoding="utf-8")
        if STITCH_SYNC_WORKFLOW.is_file()
        else ""
    )
    for needle in [
        "workflow_dispatch:",
        "secrets.STITCH_API_KEY",
        "python scripts/codex_stitch_director.py plan",
        "python scripts/codex_stitch_director.py status",
        "python scripts/codex_stitch_director.py sync",
    ]:
        if needle not in stitch_workflow:
            fail(
                f"Workflow de sincronizacao remota Stitch incompleto: {needle}", errors
            )
    for active_trigger in [
        "  push:",
        'STITCH_REMOTE_SYNC_ENABLED: "false"',
        'STITCH_COORDINATOR: "codex"',
        'STITCH_LEGACY_MODULE_SYNC_ENABLED: "false"',
    ]:
        if active_trigger not in stitch_workflow:
            fail(
                f"Workflow Stitch deve manter validacao ativa e sincronizacao remota manual: {active_trigger}",
                errors,
            )
    if "  schedule:" in stitch_workflow:
        fail("Workflow Stitch nao deve executar sincronizacao remota agendada no modo local-first.", errors)
    if "if: ${{ false }}" in stitch_workflow:
        fail("Workflow Stitch nao pode manter o job explicitamente desativado.", errors)
    if not (ROOT / "docs" / "COMPLIANCE.md").is_file():
        fail("Documento de compliance ausente: docs/COMPLIANCE.md", errors)
    if not COMPLIANCE_MATRIX.is_file():
        fail(f"Matriz de dados sensiveis ausente: {COMPLIANCE_MATRIX}", errors)
    else:
        compliance = json.loads(COMPLIANCE_MATRIX.read_text(encoding="utf-8"))
        if set(compliance.get("modules", {})) != slugs:
            fail(
                "Matriz de compliance deve cobrir exatamente os 24 modulos ativos do catalogo.",
                errors,
            )
        if (
            set(compliance.get("policy", {}).get("subject_rights", []))
            != REQUIRED_SUBJECT_RIGHTS
        ):
            fail(
                "Politica de compliance deve declarar todos os direitos do titular.",
                errors,
            )
        for slug, entry in compliance.get("modules", {}).items():
            for field in [
                "risk_level",
                "data_domains",
                "sensitive_categories",
                "legal_basis",
                "retention_policy",
                "production_gate",
            ]:
                if not entry.get(field):
                    fail(f"Matriz de compliance incompleta em {slug}.{field}.", errors)
    if not DATA_SUBJECT_RIGHTS.is_file():
        fail(f"Fluxo de direitos do titular ausente: {DATA_SUBJECT_RIGHTS}", errors)
    else:
        subject_rights = json.loads(DATA_SUBJECT_RIGHTS.read_text(encoding="utf-8"))
        if set(subject_rights.get("rights", {})) != REQUIRED_SUBJECT_RIGHTS:
            fail(
                "Fluxo de direitos do titular deve cobrir todos os direitos LGPD versionados.",
                errors,
            )
        if set(subject_rights.get("module_coverage", {})) != slugs:
            fail(
                "Fluxo de direitos do titular deve cobrir exatamente os 24 modulos ativos do catalogo.",
                errors,
            )
        guardrails = subject_rights.get("guardrails", {})
        if guardrails.get("audit_event") != "compliance.data_subject_request.processed":
            fail(
                "Fluxo de direitos do titular deve declarar evento auditavel padrao.",
                errors,
            )
    if not RETENTION_JOBS.is_file():
        fail(f"Contrato de jobs de retencao ausente: {RETENTION_JOBS}", errors)
    else:
        retention_jobs = json.loads(RETENTION_JOBS.read_text(encoding="utf-8"))
        if set(retention_jobs.get("jobs", {})) != REQUIRED_RETENTION_JOBS:
            fail(
                "Jobs de retencao devem declarar revisao, anonimizacao, descarte e legal hold.",
                errors,
            )
        if set(retention_jobs.get("module_rules", {})) != slugs:
            fail(
                "Jobs de retencao devem cobrir exatamente os 24 modulos ativos do catalogo.",
                errors,
            )
        safety = retention_jobs.get("safety_rules", {})
        if not safety.get("requires_subject_rights_link") or not safety.get(
            "requires_immutable_audit"
        ):
            fail(
                "Jobs de retencao devem exigir vinculo com direitos do titular e auditoria imutavel.",
                errors,
            )
    if not RETENTION_ALERTS.is_file():
        fail(f"Contrato de alertas de retencao ausente: {RETENTION_ALERTS}", errors)
    else:
        retention_alerts = json.loads(RETENTION_ALERTS.read_text(encoding="utf-8"))
        if set(retention_alerts.get("alerts", {})) != REQUIRED_RETENTION_ALERTS:
            fail(
                "Alertas de retencao devem cobrir falha, atraso, backlog, idade e ausencia de decisao.",
                errors,
            )
        if (
            retention_alerts.get("notification_policy", {}).get(
                "include_sensitive_payload"
            )
            is not False
        ):
            fail("Alertas de retencao nao podem incluir payload sensivel.", errors)
        for alert_name, alert in retention_alerts.get("alerts", {}).items():
            if (
                not alert.get("expr")
                or not alert.get("evidence")
                or "incident_ticket" not in alert.get("evidence", [])
            ):
                fail(f"Alerta de retencao incompleto: {alert_name}", errors)
        retention_alerting = (
            KUBERNETES_RETENTION_ALERTING.read_text(encoding="utf-8")
            if KUBERNETES_RETENTION_ALERTING.is_file()
            else ""
        )
        if (
            "kind: PrometheusRule" not in retention_alerting
            or "kind: AlertmanagerConfig" not in retention_alerting
        ):
            fail(
                "Alertas de retencao devem ter PrometheusRule e AlertmanagerConfig Kubernetes.",
                errors,
            )
        for alert_name, alert in retention_alerts.get("alerts", {}).items():
            if (
                f"alert: {alert_name}" not in retention_alerting
                or alert["expr"] not in retention_alerting
            ):
                fail(
                    f"PrometheusRule de retencao nao materializa alerta: {alert_name}",
                    errors,
                )
    if not SLO_CATALOG.is_file():
        fail(f"Catalogo SLO ausente: {SLO_CATALOG}", errors)
    else:
        slo_catalog = json.loads(SLO_CATALOG.read_text(encoding="utf-8"))
        expected_slos = {
            "api_hub_gateway_availability",
            "identity_auth_latency_p95",
            "finance_ledger_write_success",
            "outbox_delivery_freshness",
            "retention_decision_timeliness",
            "jobs_document_vault_access_audit",
        }
        if set(slo_catalog.get("slo_targets", {})) != expected_slos:
            fail(
                "Catalogo SLO deve cobrir API Hub, Identity, Finance, Outbox, Retention e Jobs.",
                errors,
            )
        if (
            slo_catalog.get("notification_policy", {}).get("include_sensitive_payload")
            is not False
        ):
            fail(
                "Catalogo SLO nao deve permitir payload sensivel em notificacoes.",
                errors,
            )
        for slo_name, slo in slo_catalog.get("slo_targets", {}).items():
            if (
                not slo.get("promql")
                or not slo.get("burn_rate_alerts")
                or "incident_ticket" not in slo.get("evidence", [])
            ):
                fail(f"SLO incompleto: {slo_name}", errors)
    if not BACKUP_RESTORE_PLAN.is_file():
        fail(f"Plano backup/restore ausente: {BACKUP_RESTORE_PLAN}", errors)
    else:
        backup_plan = json.loads(BACKUP_RESTORE_PLAN.read_text(encoding="utf-8"))
        expected_assets = {
            "postgres_core",
            "mongodb_operational",
            "private_documents",
            "gitops_configuration",
        }
        if set(backup_plan.get("assets", {})) != expected_assets:
            fail(
                "Plano backup/restore deve cobrir PostgreSQL, MongoDB, documentos privados e GitOps.",
                errors,
            )
        if (
            backup_plan.get("notification_policy", {}).get("include_sensitive_payload")
            is not False
        ):
            fail(
                "Plano backup/restore nao deve permitir payload sensivel em notificacoes.",
                errors,
            )
        for asset_name, asset in backup_plan.get("assets", {}).items():
            if not asset.get(
                "restore_validation"
            ) or "incident_ticket" not in asset.get("evidence", []):
                fail(f"Plano backup/restore incompleto para {asset_name}.", errors)
        if backup_plan.get("dr_exercise", {}).get("cadence") != "quarterly":
            fail("Exercicio DR deve ser trimestral.", errors)
    if not SENSITIVE_PERMISSIONS_REVIEW.is_file():
        fail(
            f"Revisao de permissoes sensiveis ausente: {SENSITIVE_PERMISSIONS_REVIEW}",
            errors,
        )
    else:
        permissions_review = json.loads(
            SENSITIVE_PERMISSIONS_REVIEW.read_text(encoding="utf-8")
        )
        expected_modules = {"identity", "finance", "jobs", "document", "health", "hr"}
        if set(permissions_review.get("modules", {})) != expected_modules:
            fail(
                "Revisao de permissoes sensiveis deve cobrir identity, finance, jobs, document, health e hr.",
                errors,
            )
        requirements = permissions_review.get("global_requirements", {})
        if (
            requirements.get("deny_by_default") is not True
            or requirements.get("audit_required_for_read") is not True
        ):
            fail(
                "Revisao de permissoes sensiveis deve exigir deny-by-default e auditoria de leitura.",
                errors,
            )
        for module_name, module_review in permissions_review.get("modules", {}).items():
            if not module_review.get("allowed_read_roles") or not module_review.get(
                "denied_read_roles"
            ):
                fail(
                    f"Revisao de permissoes sensiveis incompleta para {module_name}.",
                    errors,
                )
            if "audit_event_id" not in module_review.get("required_evidence", []):
                fail(
                    f"Revisao de permissoes sensiveis deve exigir audit_event_id para {module_name}.",
                    errors,
                )
    if not PERMISSIONS_ENFORCEMENT_MATRIX.is_file():
        fail(
            f"Matriz RBAC/ABAC de permissions ausente: {PERMISSIONS_ENFORCEMENT_MATRIX}",
            errors,
        )
    else:
        permissions_matrix = json.loads(
            PERMISSIONS_ENFORCEMENT_MATRIX.read_text(encoding="utf-8")
        )
        if permissions_matrix.get("module") != "permissions":
            fail("Matriz RBAC/ABAC deve declarar o modulo permissions.", errors)
        if permissions_matrix.get("deny_by_default") is not True:
            fail("Matriz RBAC/ABAC de permissions deve exigir deny_by_default.", errors)
        if set(permissions_matrix.get("resources", {})) != {
            "roles",
            "permissions",
            "user_roles",
            "access_policies",
            "approval_limits",
        }:
            fail(
                "Matriz RBAC/ABAC de permissions deve cobrir todos os recursos.", errors
            )
        if "common_user_cannot_create_role" not in permissions_matrix.get(
            "negative_tests", []
        ):
            fail(
                "Matriz RBAC/ABAC de permissions deve registrar teste negativo de escrita.",
                errors,
            )
        if (
            "administrator_with_mfa_can_create_approval_limit"
            not in permissions_matrix.get("positive_tests", [])
        ):
            fail(
                "Matriz RBAC/ABAC de permissions deve registrar teste positivo com MFA.",
                errors,
            )
    if not INCIDENT_RESPONSE_RUNBOOKS.is_file():
        fail(
            f"Catalogo de runbooks de incidente ausente: {INCIDENT_RESPONSE_RUNBOOKS}",
            errors,
        )
    else:
        incident_runbooks = json.loads(
            INCIDENT_RESPONSE_RUNBOOKS.read_text(encoding="utf-8")
        )
        expected_runbooks = {
            "security_sensitive_access",
            "payments_ledger_integrity",
            "outbox_delivery_failure",
            "retention_lgpd_failure",
            "backup_restore_dr",
            "slo_burn_rate",
        }
        if set(incident_runbooks.get("runbooks", {})) != expected_runbooks:
            fail(
                "Catalogo de incidentes deve cobrir seguranca, pagamentos, outbox, retencao, DR e SLO.",
                errors,
            )
        if (
            incident_runbooks.get("notification_policy", {}).get(
                "include_sensitive_payload"
            )
            is not False
        ):
            fail(
                "Catalogo de incidentes nao deve permitir payload sensivel em notificacoes.",
                errors,
            )
        for runbook_name, runbook in incident_runbooks.get("runbooks", {}).items():
            if not runbook.get("containment") or "incident_ticket" not in runbook.get(
                "evidence", []
            ):
                fail(f"Runbook de incidente incompleto: {runbook_name}.", errors)
            if (
                runbook.get("severity") == "critical"
                and runbook.get("postmortem_required") is not True
            ):
                fail(
                    f"Incidente critico deve exigir postmortem: {runbook_name}.", errors
                )
    if not LOAD_TEST_PLAN.is_file():
        fail(f"Plano de testes de carga ausente: {LOAD_TEST_PLAN}", errors)
    else:
        load_plan = json.loads(LOAD_TEST_PLAN.read_text(encoding="utf-8"))
        expected_scenarios = {
            "api_hub_gateway_catalog",
            "identity_auth_mfa",
            "finance_escrow_ledger",
            "jobs_resume_access",
            "retention_worker_batch",
        }
        if set(load_plan.get("scenarios", {})) != expected_scenarios:
            fail(
                "Plano de carga deve cobrir API Hub, Identity, Finance, Jobs e Retention.",
                errors,
            )
        policy = load_plan.get("execution_policy", {})
        if (
            policy.get("no_real_payment_capture") is not True
            or policy.get("no_sensitive_payload_capture") is not True
        ):
            fail(
                "Plano de carga deve bloquear captura real de pagamento e payload sensivel.",
                errors,
            )
        for scenario_name, scenario in load_plan.get("scenarios", {}).items():
            if not scenario.get("required_metrics") or "run_id" not in scenario.get(
                "evidence", []
            ):
                fail(f"Cenario de carga incompleto: {scenario_name}.", errors)
            if "payload" in " ".join(scenario.get("evidence", [])).casefold():
                fail(
                    f"Cenario de carga nao deve exigir evidencia com payload: {scenario_name}.",
                    errors,
                )

    if errors:
        print("\nFalhas de validacao encontradas:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "\nRepositorio validado com sucesso! Todos os 24 modulos ativos e a infraestrutura estao em conformidade."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
