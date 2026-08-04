#!/usr/bin/env python3
"""Falha o release quando o Valley perde telas, servidor, ações ou branding obrigatório."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "apps" / "valley" / "src"
ACTIVE_TSX = [
    APP_ROOT / "App.tsx",
    APP_ROOT / "ui.tsx",
    *(APP_ROOT / "views").glob("*.tsx"),
    *(APP_ROOT / "components").glob("*.tsx"),
]
MAIN = APP_ROOT / "main.tsx"
BRIDGE = APP_ROOT / "lib" / "nativeBridge.ts"
FLUTTER_ROOT = ROOT / "apps" / "valley-flutter" / "lib"
FLUTTER_FILES = [FLUTTER_ROOT / "main.dart", FLUTTER_ROOT / "api_bridge.dart"]
WORKFLOW = ROOT / ".github" / "workflows" / "valley-android-release.yml"
COORDINATE = ROOT / "config" / "stitch" / "template_project_coordinate.json"
LOGO = ROOT / "assets" / "brand" / "valley-logo-official.png"

SCREEN_KEYS = {
    "shell_onboarding_identity": (
        "AuthScreen",
        "ValleyAvatarPicker",
        "/registrations",
        "/auth/login",
    ),
    "home_discovery_catalog": (
        "ConsumerHome",
        "Ver todos os módulos",
        "ProductFeed",
        "/gateway/catalog/offers",
    ),
    "commerce_checkout_wallet": (
        "FinanceView",
        "/gateway/catalog/actions",
        "/marketplace/resources/carts",
    ),
    "services_schedule": (
        "ServicesView",
        "/services/resources/",
        "Falar com o fornecedor",
    ),
    "delivery_tracking": (
        "DeliveryView",
        "module='delivery'",
        "resource='delivery_requests'",
    ),
    "mobility": (
        "MobilityView",
        "module='mobility'",
        "useState<'rides'|'tickets'>",
    ),
    "jobs_health_documents": (
        "JobsView",
        "HealthView",
        "LifeView",
        "/jobs/resources/resumes",
        "imports/ctps-digital",
    ),
    "notifications_support_settings": (
        "SettingsView",
        "/gateway/status",
    ),
}


def read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Arquivo obrigatório ausente: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, values: tuple[str, ...] | list[str], source: str) -> None:
    missing = [value for value in values if value not in text]
    if missing:
        raise SystemExit(f"{source} não cobre: {', '.join(missing)}")


def validate_buttons(app: str) -> None:
    opening_tags = re.findall(r"<button\b[^>]*>", app, flags=re.DOTALL)
    if not opening_tags:
        raise SystemExit("Nenhum botão encontrado na interface Valley.")
    dead = []
    for tag in opening_tags:
        compact = re.sub(r"\s+", " ", tag)
        if not re.search(r"type=['\"]submit['\"]", tag) and "onClick=" not in tag:
            dead.append(compact[:180])
    if dead:
        raise SystemExit("Botões sem ação real encontrados:\n" + "\n".join(dead))


def main() -> None:
    app = "\n".join(read(path) for path in ACTIVE_TSX)
    main_tsx = read(MAIN)
    bridge = read(BRIDGE)
    flutter = "\n".join(read(path) for path in FLUTTER_FILES)
    workflow = read(WORKFLOW)
    coordinate = read(COORDINATE)

    if not LOGO.is_file():
        raise SystemExit("Logomarca oficial Valley ausente.")

    for key, evidence in SCREEN_KEYS.items():
        if key not in coordinate:
            raise SystemExit(f"Tela Stitch ausente da coordenada: {key}")
        assert_contains(app, evidence, f"Tela {key}")

    validate_buttons(app)

    forbidden = (
        "setTimeout(() => setLoading(false)",
        "Modo demonstração ativo",
        "valley-logo-transparent.svg",
    )
    present = [value for value in forbidden if value in app]
    if present:
        raise SystemExit(
            "Implementações simuladas, placeholders ou marca não autorizada: "
            + ", ".join(present)
        )

    assert_contains(
        app,
        (
            "/auth/refresh",
            "/auth/logout",
            "/gateway/consumer/orders",
            "/gateway/consumer/orders/",
            "/identity/mfa/setup",
            "/identity/mfa/verify",
            "radius_km: '10'",
            "safeMonthlyLimit",
            "purchase_power_consent",
            "canComment",
            "onAddToCart",
            "onSupplier",
            "valley-logo-official.png",
        ),
        "Aplicativo",
    )
    assert_contains(main_tsx, ("installNativeFetchBridge", "experience.css"), "Bootstrap web")
    assert_contains(
        bridge,
        (
            "https://all-in-one-api-hub.web.app",
            "ValleyNative",
            "X-Valley-Api-Version",
            "verifyCriticalResponse",
            "Ed25519",
            "bodyBase64",
        ),
        "Ponte servidor",
    )
    assert_contains(
        flutter,
        (
            "HttpClient",
            "ValleyNative",
            "https://all-in-one-api-hub.web.app",
            "assets/brand/valley-logo-official.png",
            "bodyBase64",
        ),
        "Shell Android",
    )
    if 'VITE_VALLEY_ALLOW_DEMO: "true"' in workflow:
        raise SystemExit("Release Android não pode habilitar fallback demonstrativo.")
    assert_contains(
        workflow,
        (
            "configure_valley_flutter_android.py",
            "validate_valley_functional_completeness.py",
            "VITE_API_HUB_URL: https://all-in-one-api-hub.web.app",
        ),
        "Workflow Android",
    )
    print(
        f"Valley validado: {len(SCREEN_KEYS)} grupos Stitch e "
        f"{len(re.findall(r'<button\\b', app))} botões com ação."
    )


if __name__ == "__main__":
    main()
