"""Runtime compartilhado pelos microservicos All-in-One."""

from __future__ import annotations

from fastapi import FastAPI

from . import runtime as _runtime

_original_create_module_app = _runtime.create_module_app


def _create_module_app_with_extensions(
    module_name: str, version: str = "0.2.0"
) -> FastAPI:
    app = _original_create_module_app(module_name, version)
    if module_name == "marketplace":
        from checkout_routes import register_checkout_routes

        app.version = "0.4.0"
        register_checkout_routes(app)
    return app


_runtime.create_module_app = _create_module_app_with_extensions
