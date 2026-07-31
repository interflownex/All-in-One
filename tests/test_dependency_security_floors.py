from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", value))


def package_version(lock_path: Path, package: str) -> str | None:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    entry = lock["packages"].get(f"node_modules/{package}")
    return str(entry["version"]) if entry else None


def test_npm_lockfiles_respect_security_floors() -> None:
    lockfiles = [
        *sorted((ROOT / "apps").glob("*/package-lock.json")),
        ROOT / "desktop" / "valley-erp" / "package-lock.json",
    ]
    floors = {
        "postcss": (8, 5, 18),
        "brace-expansion": (5, 0, 7),
    }
    for lock_path in lockfiles:
        for package, minimum in floors.items():
            version = package_version(lock_path, package)
            if version:
                assert version_tuple(version) >= minimum, f"{lock_path}: {package}={version}"


def test_react_router_spas_use_patched_v7_release() -> None:
    for app in ("all-in-one", "all-in-one-user", "all-in-one-business"):
        lock_path = ROOT / "apps" / app / "package-lock.json"
        assert package_version(lock_path, "react-router") == "7.18.2"
        assert package_version(lock_path, "react-router-dom") == "7.18.2"


def test_admin_vite_uses_patched_release() -> None:
    lock_path = ROOT / "apps" / "all-in-one-admin" / "package-lock.json"
    assert version_tuple(package_version(lock_path, "vite") or "0") >= (8, 0, 16)


def test_android_build_graph_declares_hardened_transitive_versions() -> None:
    build_script = (ROOT / "apps" / "valley-android" / "build.gradle.kts").read_text(
        encoding="utf-8"
    )
    required = (
        "io.netty:netty-codec-http:4.1.136.Final",
        "io.netty:netty-codec-http2:4.1.136.Final",
        "org.bouncycastle:bcpkix-jdk18on:1.84",
        "org.bouncycastle:bcprov-jdk18on:1.84",
        "org.bitbucket.b_c:jose4j:0.9.6",
        "org.jdom:jdom2:2.0.6.1",
        "org.apache.commons:commons-lang3:3.18.0",
        "org.apache.httpcomponents:httpclient:4.5.14",
        "com.google.protobuf:protobuf-java:3.25.5",
        "com.google.guava:guava:33.3.1-jre",
    )
    assert all(marker in build_script for marker in required)


def test_valley_session_remains_in_memory_and_clears_legacy_storage() -> None:
    source = (ROOT / "apps" / "valley" / "src" / "lib" / "api.ts").read_text(
        encoding="utf-8"
    )
    assert "let activeSession: Session | null = null" in source
    assert "activeSession = session" in source
    assert "localStorage.setItem(SESSION_KEY" not in source
    assert "localStorage.getItem(SESSION_KEY" not in source
    assert "window.localStorage.removeItem(key)" in source
