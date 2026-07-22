from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent


@lru_cache
def client_for(slug: str) -> TestClient:
    return _build_client(slug)


def fresh_client_for(slug: str) -> TestClient:
    return _build_client(slug)


def _build_client(slug: str) -> TestClient:
    path = ROOT / "modules" / slug / "main.py"
    module_dir = str(path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location(f"all_in_one_{slug}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Modulo indisponivel: {slug}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)
