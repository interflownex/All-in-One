#!/usr/bin/env python3
"""Falha quando o contrato minimo de seguranca do APK Valley regride."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "apps" / "valley-android"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "valley-android-release.yml"
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
DAST_WORKFLOW = ROOT / ".github" / "workflows" / "valley-dast.yml"


def require(text: str, marker: str, source: Path, errors: list[str]) -> None:
    if marker not in text:
        errors.append(f"{source.relative_to(ROOT)}: marcador obrigatorio ausente: {marker}")


def validate() -> list[str]:
    errors: list[str] = []
    gradle_path = ANDROID / "app" / "build.gradle.kts"
    manifest_path = ANDROID / "app" / "src" / "main" / "AndroidManifest.xml"
    network_path = ANDROID / "app" / "src" / "main" / "res" / "xml" / "network_security_config.xml"
    source_root = ANDROID / "app" / "src" / "main" / "java"
    secure_store_path = source_root / "com" / "example" / "valley" / "security" / "SecureSessionStore.kt"
    integrity_path = source_root / "com" / "example" / "valley" / "security" / "PlayIntegrityAttestor.kt"
    runtime_integrity_path = source_root / "com" / "example" / "valley" / "security" / "RuntimeIntegrityGuard.kt"
    observability_path = source_root / "com" / "example" / "valley" / "observability" / "ValleyObservability.kt"
    observability_contract_path = ROOT / "config" / "observability" / "valley_mobile_observability.json"
    play_integrity_server_path = ROOT / "modules" / "identity" / "play_integrity.py"
    identity_main_path = ROOT / "modules" / "identity" / "main.py"
    play_integrity_policy_path = ROOT / "config" / "security" / "valley_play_integrity_policy.json"
    identity_manifest_path = ROOT / "infra" / "kubernetes" / "base" / "identity.yaml"
    dast_policy_path = ROOT / "config" / "security" / "valley_dast_policy.json"
    response_signing_path = ROOT / "modules" / "shared" / "response_signing.py"
    media_cdn_path = ROOT / "modules" / "shared" / "media_cdn.py"
    api_hub_path = ROOT / "modules" / "api_hub" / "main.py"
    api_hub_manifest_path = ROOT / "infra" / "kubernetes" / "base" / "api-hub.yaml"
    catalog_source = ROOT / "apps" / "valley" / "src"
    gradle = gradle_path.read_text(encoding="utf-8")
    manifest = manifest_path.read_text(encoding="utf-8")
    network = network_path.read_text(encoding="utf-8")
    secure_store = secure_store_path.read_text(encoding="utf-8")
    integrity = integrity_path.read_text(encoding="utf-8")
    runtime_integrity = runtime_integrity_path.read_text(encoding="utf-8")
    observability = observability_path.read_text(encoding="utf-8")
    observability_contract = observability_contract_path.read_text(encoding="utf-8")
    play_integrity_server = play_integrity_server_path.read_text(encoding="utf-8")
    identity_main = identity_main_path.read_text(encoding="utf-8")
    play_integrity_policy = play_integrity_policy_path.read_text(encoding="utf-8")
    identity_manifest = identity_manifest_path.read_text(encoding="utf-8")
    dast_policy = dast_policy_path.read_text(encoding="utf-8")
    response_signing = response_signing_path.read_text(encoding="utf-8")
    media_cdn = media_cdn_path.read_text(encoding="utf-8")
    api_hub = api_hub_path.read_text(encoding="utf-8")
    api_hub_manifest = api_hub_manifest_path.read_text(encoding="utf-8")
    release_workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    security_workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")
    dast_workflow = DAST_WORKFLOW.read_text(encoding="utf-8")

    for marker in (
        'create("staging")',
        "isDebuggable = false",
        "isMinifyEnabled = true",
        "isShrinkResources = true",
        'signingConfigs.findByName("release")',
        "releaseRequested && !releaseSigningPropertiesFile.isFile",
        "VALLEY_PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER",
        "releaseRequested && playIntegrityCloudProjectNumber == \"0\"",
        "VALLEY_PLAY_APP_SIGNING_CERT_SHA256",
        "releaseRequested && !releaseCertificateSha256.matches",
        "implementation(libs.play.integrity)",
        "implementation(libs.firebase.analytics)",
        "implementation(libs.firebase.crashlytics)",
        "alias(libs.plugins.firebase.crashlytics)",
    ):
        require(gradle, marker, gradle_path, errors)
    if re.search(r"release\s*\{[^}]*signingConfig\s*=\s*signingConfigs\.getByName\(\"debug\"\)", gradle, re.S):
        errors.append("release referencia explicitamente a assinatura debug")
    if re.search(r"packaging\s*\{[^}]*keepDebugSymbols", gradle, re.S):
        errors.append("configuracao global preserva simbolos nativos no release")
    require(
        gradle,
        'selector().withBuildType("debug")',
        gradle_path,
        errors,
    )
    for flavor in ("staging", "production"):
        require(
            gradle,
            f'create("{flavor}")',
            gradle_path,
            errors,
        )

    for marker in (
        'android:allowBackup="false"',
        'android:fullBackupContent="false"',
        'android:usesCleartextTraffic="false"',
        'android:networkSecurityConfig="@xml/network_security_config"',
        'android:name="firebase_analytics_collection_enabled"',
        'android:name="firebase_crashlytics_collection_enabled"',
        'android:name="google_analytics_adid_collection_enabled"',
        'android:name="com.google.android.gms.permission.AD_ID" tools:node="remove"',
        'android:name="android.permission.ACCESS_ADSERVICES_AD_ID" tools:node="remove"',
        'android:name="android.permission.ACCESS_ADSERVICES_ATTRIBUTION" tools:node="remove"',
    ):
        require(manifest, marker, manifest_path, errors)
    require(network, 'cleartextTrafficPermitted="false"', network_path, errors)

    for marker in ("AndroidKeyStore", "AES/GCM/NoPadding", "KeyGenParameterSpec", "setKeySize(256)"):
        require(secure_store, marker, secure_store_path, errors)
    for marker in ('getString("refresh_token")', '.put("refresh_token", session.refreshToken)', 'getString("session_id")'):
        require(secure_store, marker, secure_store_path, errors)
    for marker in ("IntegrityManagerFactory.createStandard", "setCloudProjectNumber", "setRequestHash"):
        require(integrity, marker, integrity_path, errors)
    for marker in (
        "if (BuildConfig.DEBUG)",
        "Debug.isDebuggerConnected()",
        'File("/proc/self/status")',
        'File("/proc/self/maps")',
        '"frida"',
        '"xposed"',
        '"zygisk"',
        "PackageManager.CERT_INPUT_SHA256",
        "BuildConfig.PLAY_APP_SIGNING_CERT_SHA256",
    ):
        require(runtime_integrity, marker, runtime_integrity_path, errors)
    for marker in (
        "setAnalyticsCollectionEnabled(consent.decided && consent.analytics)",
        "setCrashlyticsCollectionEnabled(consent.decided && consent.crashReports)",
        "deleteUnsentReports()",
        "resetAnalyticsData()",
        "ALLOW_AD_PERSONALIZATION_SIGNALS",
        '"api_request_completed"',
        '"correlation_id"',
    ):
        require(observability, marker, observability_path, errors)
    for marker in (
        '"default_collection_enabled": false',
        '"granular_consent"',
        '"forbidden_fields"',
        '"mobile_api_availability"',
        '"mobile_api_latency_p95"',
    ):
        require(observability_contract, marker, observability_contract_path, errors)
    for marker in (
        "decodeIntegrityToken",
        "PLAY_RECOGNIZED",
        "MEETS_DEVICE_INTEGRITY",
        "certificateSha256Digest",
        "requestPackageName",
        "requestHash",
        "timestampMillis",
        "UNKNOWN_CAPTURING",
        "UNKNOWN_CONTROLLING",
        "google.auth.default",
    ):
        require(play_integrity_server, marker, play_integrity_server_path, errors)
    for marker in (
        'request.headers.get("X-Play-Integrity-Token")',
        "Depends(require_play_integrity)",
        'app.extra["play_integrity_verifier"]',
    ):
        require(identity_main, marker, identity_main_path, errors)
    for route in ("/registrations", "/auth/login", "/auth/refresh", "/auth/logout"):
        require(play_integrity_policy, route, play_integrity_policy_path, errors)
    for marker in (
        "serviceAccountName: identity-play-integrity",
        "iam.gke.io/gcp-service-account",
    ):
        require(identity_manifest, marker, identity_manifest_path, errors)

    kotlin_sources = "\n".join(path.read_text(encoding="utf-8") for path in source_root.rglob("*.kt"))
    if re.search(r'putString\(\s*"(?:token|password|refresh_token)"', kotlin_sources):
        errors.append("credencial sensivel persiste em SharedPreferences sem envelope criptografado")
    if "buildDemoSession(" in kotlin_sources:
        errors.append("aplicativo Android ainda aceita sessao local simulada quando o backend falha")
    for marker in ("/auth/refresh", "/auth/logout", "X-Device-Fingerprint", "X-Correlation-Id", "/health"):
        if marker not in kotlin_sources:
            errors.append(f"cliente Android nao implementa contrato de sessao obrigatorio: {marker}")
    for marker in (
        "DisposableEffect(lifecycleOwner)",
        "Lifecycle.Event.ON_STOP -> webView?.onPause()",
        "settings.cacheMode = WebSettings.LOAD_DEFAULT",
        "settings.mediaPlaybackRequiresUserGesture = true",
        "setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_BOUND, true)",
        "stopLoading()",
        "destroy()",
    ):
        if marker not in kotlin_sources:
            errors.append(f"WebView Android sem requisito de memoria/ciclo de vida: {marker}")

    for marker in (
        "VALLEY_RELEASE_KEYSTORE_BASE64",
        "VALLEY_PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER",
        "VALLEY_PLAY_APP_SIGNING_CERT_SHA256",
        "testReleaseUnitTest assembleRelease bundleRelease",
        "--require-release-signature",
        "anchore/sbom-action@v0",
        "actions/attest-build-provenance@v2",
        "google-play-production",
    ):
        require(release_workflow, marker, RELEASE_WORKFLOW, errors)
    for marker in (
        "github/codeql-action/init@v4",
        "languages: java-kotlin",
        "gradle/actions/dependency-submission@v6",
        "testDebugUnitTest lintDebug assembleDebug",
        "github/codeql-action/analyze@v4",
    ):
        require(security_workflow, marker, SECURITY_WORKFLOW, errors)
    for marker in (
        "zaproxy/action-full-scan@v0.13.0",
        "allow_issue_writing: false",
        "fail_action: false",
        'cmd_options: "-a -m 2 -T 5"',
        "scripts/evaluate_zap_report.py",
        "--fail-at high",
    ):
        require(dast_workflow, marker, DAST_WORKFLOW, errors)
    for marker in (
        '"active_scan": true',
        '"production_scan_allowed": false',
        '"pentest_equivalence": false',
    ):
        require(dast_policy, marker, dast_policy_path, errors)
    for marker in (
        "Ed25519PrivateKey",
        "VALLEY_RESPONSE_SIGNING_PRIVATE_KEY_B64",
        "canonical_response",
        "X-Valley-Response-Signature",
        "obrigatoria em producao",
    ):
        require(response_signing, marker, response_signing_path, errors)
    for marker in (
        "/gateway/security/response-signing-key",
        "signed_json_response",
        "expose_headers",
    ):
        require(api_hub, marker, api_hub_path, errors)
    for marker in (
        "ALL_IN_ONE_ENVIRONMENT",
        "VALLEY_RESPONSE_SIGNING_PRIVATE_KEY_B64",
        "name: valley-response-signing",
        "key: private-key-b64",
    ):
        require(api_hub_manifest, marker, api_hub_manifest_path, errors)
    for marker in (
        "VALLEY_MEDIA_CDN_BASE_URL",
        'parsed.scheme != "https"',
        "normalize_offer_media",
        "IMAGE_EXTENSIONS",
        "VIDEO_EXTENSIONS",
    ):
        require(media_cdn, marker, media_cdn_path, errors)
    for marker in ("VALLEY_MEDIA_CDN_BASE_URL", "configMapKeyRef", "name: valley-media-cdn", "key: base-url"):
        require(api_hub_manifest, marker, api_hub_manifest_path, errors)

    web_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in catalog_source.rglob("*")
        if path.is_file() and path.suffix in {".ts", ".tsx"}
    )
    if re.search(r'localStorage\.(?:getItem|setItem)\(\s*[\'\"]valley\.session\.(?:token|user-id)', web_sources):
        errors.append("sessao web sensivel persiste em localStorage")
    if "ws://localhost" in web_sources or "http://localhost" in web_sources:
        errors.append("fonte Valley contem endpoint local inseguro que pode vazar para o APK")
    for marker in (
        "import.meta.env.DEV && import.meta.env.VITE_VALLEY_ALLOW_DEMO === 'true'",
        "CATALOG_CACHE_TTL_MS",
        "params.append('offset'",
        'loading="lazy"',
        'preload="none"',
        "Carregar mais ofertas",
        "verifyCriticalResponse",
        "window.crypto.subtle.verify('Ed25519'",
        "RESPONSE_SIGNATURE_MAX_AGE_SECONDS",
        "safeMediaUrl",
    ):
        if marker not in web_sources:
            errors.append(f"frontend Valley sem requisito de catálogo/performance: {marker}")

    embedded_web = ANDROID / "app" / "src" / "main" / "assets" / "valley"
    embedded_javascript = "\n".join(path.read_text(encoding="utf-8") for path in embedded_web.rglob("*.js"))
    if "VITE_VALLEY_ALLOW_DEMO" in embedded_javascript:
        errors.append("bundle Android permite alterar o modo demonstrativo em tempo de execução")
    embedded_brand = embedded_web / "assets" / "brand"
    required_optimized_brand = {
        "all-in-one-logo-light-official.webp",
        "valley-logo-official.webp",
    }
    present_optimized_brand = {path.name for path in embedded_brand.glob("*.webp")}
    if not required_optimized_brand.issubset(present_optimized_brand):
        errors.append("bundle Android não contém todos os logotipos WebP otimizados")
    embedded_pngs = sorted(path.name for path in embedded_brand.glob("*.png"))
    if embedded_pngs:
        errors.append("bundle Android ainda contém logotipos PNG não otimizados: " + ", ".join(embedded_pngs))
    oversized_brand = sorted(
        path.name for path in embedded_brand.glob("*.webp") if path.stat().st_size > 50_000
    )
    if oversized_brand:
        errors.append("logotipos WebP excedem 50 KB: " + ", ".join(oversized_brand))

    permission_tags = re.findall(r"<uses-permission[^>]+>", manifest)
    permissions = [
        match.group(1)
        for tag in permission_tags
        if 'tools:node="remove"' not in tag
        if (match := re.search(r'android:name="([^"]+)"', tag))
    ]
    unexpected = sorted(set(permissions) - {"android.permission.INTERNET"})
    if unexpected:
        errors.append("permissoes Android fora da allowlist: " + ", ".join(unexpected))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Contrato de release Valley reprovado:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Contrato de release Valley aprovado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
