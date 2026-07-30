"""Runtime compartilhado pelos microservicos All-in-One."""

from . import runtime as _runtime

_ORIGINAL_CREATE_MODULE_APP = _runtime.create_module_app


def _create_module_app_with_specialized_routes(
    module_name: str, version: str = "0.2.0"
):
    app = _ORIGINAL_CREATE_MODULE_APP(module_name, version)
    if module_name == "marketplace":
        from .marketplace_checkout_routes import register_marketplace_checkout_routes

        register_marketplace_checkout_routes(app)
    return app


_runtime.create_module_app = _create_module_app_with_specialized_routes
