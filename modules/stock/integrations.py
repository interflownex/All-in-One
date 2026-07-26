from __future__ import annotations

import hashlib
import hmac
import json
import os
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

ProviderSlug = Literal["cj_dropshipping", "aliexpress"]
ProviderEnvironment = Literal["sandbox", "production"]
SyncResource = Literal["products", "inventory", "prices", "orders", "tracking"]

router = APIRouter(prefix="/integrations", tags=["stock-integrations"])


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _default_config_path() -> Path:
    return Path(
        os.getenv(
            "STOCK_INTEGRATIONS_CONFIG_PATH",
            "/var/lib/all-in-one/stock-integrations.json",
        )
    )


def _default_secrets_path() -> Path:
    return Path(
        os.getenv(
            "STOCK_INTEGRATIONS_SECRETS_PATH",
            "/var/lib/all-in-one/stock-integration-secrets.enc",
        )
    )


PROVIDER_MANIFESTS: dict[ProviderSlug, dict[str, Any]] = {
    "cj_dropshipping": {
        "display_name": "CJ Dropshipping",
        "docs_url": "https://developers.cjdropshipping.com/en/api/api2/",
        "auth_kind": "api_key_to_access_token",
        "default_api_base_url": "https://developers.cjdropshipping.com",
        "default_authorization_url": None,
        "default_token_url": "https://developers.cjdropshipping.com/api2.0/v1/authentication/getAccessToken",
        "default_refresh_url": "https://developers.cjdropshipping.com/api2.0/v1/authentication/refreshAccessToken",
        "connection_test_path": "/api2.0/v1/setting/get",
        "secret_env_defaults": {
            "api_key": "CJ_DROPSHIPPING_API_KEY",
            "access_token": "CJ_DROPSHIPPING_ACCESS_TOKEN",
            "refresh_token": "CJ_DROPSHIPPING_REFRESH_TOKEN",
            "webhook_secret": "CJ_DROPSHIPPING_WEBHOOK_SECRET",
        },
        "required_for_connection": ["api_key"],
        "capabilities": ["products", "inventory", "prices", "orders", "tracking"],
        "endpoints": {
            "categories": "/api2.0/v1/product/getCategory",
            "products": "/api2.0/v1/product/listV2",
            "product_detail": "/api2.0/v1/product/query",
            "variants": "/api2.0/v1/product/variant/query",
            "inventory": "/api2.0/v1/product/stock/getInventoryByPid",
            "create_order": "/api2.0/v1/shopping/order/createOrderV2",
            "orders": "/api2.0/v1/shopping/order/list",
            "order_detail": "/api2.0/v1/shopping/order/getOrderDetail",
            "freight": "/api2.0/v1/logistic/freightCalculate",
            "tracking": "/api2.0/v1/logistic/trackInfo",
        },
    },
    "aliexpress": {
        "display_name": "AliExpress Open Platform",
        "docs_url": "https://developer.alibaba.com/docs/doc.htm?articleId=120672&docType=1&treeId=727",
        "auth_kind": "oauth2_authorization_code_signed_gateway",
        "default_api_base_url": "https://api-sg.aliexpress.com",
        "default_authorization_url": "https://api-sg.aliexpress.com/oauth/authorize",
        "default_token_url": "https://api-sg.aliexpress.com/rest/auth/token/create",
        "default_refresh_url": "https://api-sg.aliexpress.com/rest/auth/token/refresh",
        "connection_test_path": None,
        "secret_env_defaults": {
            "app_key": "ALIEXPRESS_APP_KEY",
            "app_secret": "ALIEXPRESS_APP_SECRET",
            "access_token": "ALIEXPRESS_ACCESS_TOKEN",
            "refresh_token": "ALIEXPRESS_REFRESH_TOKEN",
            "webhook_secret": "ALIEXPRESS_WEBHOOK_SECRET",
        },
        "required_for_connection": ["app_key", "app_secret"],
        "capabilities": ["products", "inventory", "prices", "orders", "tracking"],
        "endpoints": {
            "oauth_authorize": "/oauth/authorize",
            "oauth_token": "/rest/auth/token/create",
            "oauth_refresh": "/rest/auth/token/refresh",
            "gateway": "/sync",
        },
    },
}


class ProviderConfig(BaseModel):
    provider: ProviderSlug
    enabled: bool = False
    environment: ProviderEnvironment = "sandbox"
    api_base_url: str
    authorization_url: str | None = None
    token_url: str | None = None
    refresh_url: str | None = None
    callback_url: str | None = None
    webhook_url: str | None = None
    secret_env: dict[str, str] = Field(default_factory=dict)
    auto_sync_products: bool = False
    auto_sync_inventory: bool = False
    auto_sync_prices: bool = False
    auto_sync_orders: bool = False
    auto_sync_tracking: bool = False
    auto_publish_products: bool = False
    schedule_minutes: int = Field(default=60, ge=5, le=10080)
    timeout_seconds: int = Field(default=20, ge=3, le=120)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    rate_limit_per_minute: int = Field(default=30, ge=1, le=1000)
    max_products_per_run: int = Field(default=100, ge=1, le=1000)
    source_currency: str = Field(default="USD", min_length=3, max_length=3)
    target_currency: str = Field(default="BRL", min_length=3, max_length=3)
    default_country: str = Field(default="BR", min_length=2, max_length=2)
    default_warehouse: str | None = Field(default=None, max_length=120)
    markup_percent: float = Field(default=0, ge=0, le=1000)
    connection_test_path: str | None = Field(default=None, max_length=240)
    mapping_rules: dict[str, str] = Field(default_factory=dict)
    provider_options: dict[str, str | int | float | bool] = Field(default_factory=dict)
    updated_at: str = Field(default_factory=_now)
    updated_by: str = "system"

    @field_validator(
        "api_base_url",
        "authorization_url",
        "token_url",
        "refresh_url",
        "callback_url",
        "webhook_url",
    )
    @classmethod
    def validate_https_url(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if not value.startswith("https://"):
            raise ValueError("URLs de integracao devem usar HTTPS.")
        return value.rstrip("/")

    @field_validator("source_currency", "target_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("default_country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.upper()


class ProviderConfigPatch(BaseModel):
    enabled: bool | None = None
    environment: ProviderEnvironment | None = None
    api_base_url: str | None = None
    authorization_url: str | None = None
    token_url: str | None = None
    refresh_url: str | None = None
    callback_url: str | None = None
    webhook_url: str | None = None
    secret_env: dict[str, str] | None = None
    auto_sync_products: bool | None = None
    auto_sync_inventory: bool | None = None
    auto_sync_prices: bool | None = None
    auto_sync_orders: bool | None = None
    auto_sync_tracking: bool | None = None
    auto_publish_products: bool | None = None
    schedule_minutes: int | None = Field(default=None, ge=5, le=10080)
    timeout_seconds: int | None = Field(default=None, ge=3, le=120)
    retry_attempts: int | None = Field(default=None, ge=0, le=10)
    rate_limit_per_minute: int | None = Field(default=None, ge=1, le=1000)
    max_products_per_run: int | None = Field(default=None, ge=1, le=1000)
    source_currency: str | None = Field(default=None, min_length=3, max_length=3)
    target_currency: str | None = Field(default=None, min_length=3, max_length=3)
    default_country: str | None = Field(default=None, min_length=2, max_length=2)
    default_warehouse: str | None = Field(default=None, max_length=120)
    markup_percent: float | None = Field(default=None, ge=0, le=1000)
    connection_test_path: str | None = Field(default=None, max_length=240)
    mapping_rules: dict[str, str] | None = None
    provider_options: dict[str, str | int | float | bool] | None = None


class ProviderSecretsInput(BaseModel):
    api_key: str | None = Field(default=None, min_length=3, max_length=1000)
    app_key: str | None = Field(default=None, min_length=3, max_length=1000)
    app_secret: str | None = Field(default=None, min_length=3, max_length=2000)
    access_token: str | None = Field(default=None, min_length=3, max_length=4000)
    refresh_token: str | None = Field(default=None, min_length=3, max_length=4000)
    webhook_secret: str | None = Field(default=None, min_length=8, max_length=2000)

    def non_empty(self) -> dict[str, str]:
        return {
            key: value
            for key, value in self.model_dump().items()
            if isinstance(value, str) and value.strip()
        }


class SecretClearRequest(BaseModel):
    names: list[str] = Field(min_length=1, max_length=10)


class SyncRequest(BaseModel):
    resources: list[SyncResource] = Field(default_factory=lambda: ["products"])
    dry_run: bool = True
    query: str | None = Field(default=None, max_length=200)
    product_id: str | None = Field(default=None, max_length=200)
    order_id: str | None = Field(default=None, max_length=200)
    tracking_number: str | None = Field(default=None, max_length=200)
    limit: int = Field(default=20, ge=1, le=100)


class OAuthCallbackRequest(BaseModel):
    code: str = Field(min_length=3, max_length=2000)


class IntegrationStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _default_config_path()
        self._lock = threading.RLock()
        self._state = self._load()

    def _default_provider(self, provider: ProviderSlug) -> ProviderConfig:
        manifest = PROVIDER_MANIFESTS[provider]
        return ProviderConfig(
            provider=provider,
            api_base_url=manifest["default_api_base_url"],
            authorization_url=manifest["default_authorization_url"],
            token_url=manifest["default_token_url"],
            refresh_url=manifest["default_refresh_url"],
            connection_test_path=manifest["connection_test_path"],
            secret_env=dict(manifest["secret_env_defaults"]),
            mapping_rules={
                "sku": "source_sku",
                "title": "source_title",
                "description": "source_description",
                "images": "source_images",
                "price": "source_price",
                "inventory": "source_inventory",
                "tracking": "source_tracking",
            },
        )

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "providers": {
                provider: self._default_provider(provider).model_dump(mode="json")
                for provider in PROVIDER_MANIFESTS
            },
            "runs": [],
            "audit": [],
        }

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return self._default_state()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("estado invalido")
        except (OSError, ValueError, json.JSONDecodeError):
            return self._default_state()
        default = self._default_state()
        for provider, config in default["providers"].items():
            raw.setdefault("providers", {}).setdefault(provider, config)
        raw.setdefault("runs", [])
        raw.setdefault("audit", [])
        raw.setdefault("schema_version", 1)
        return raw

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            delete=False,
        ) as handle:
            json.dump(self._state, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, self.path)

    def get_config(self, provider: ProviderSlug) -> ProviderConfig:
        with self._lock:
            return ProviderConfig.model_validate(self._state["providers"][provider])

    def list_configs(self) -> list[ProviderConfig]:
        return [self.get_config(provider) for provider in PROVIDER_MANIFESTS]

    def patch_config(
        self,
        provider: ProviderSlug,
        patch: ProviderConfigPatch,
        actor: str,
    ) -> ProviderConfig:
        with self._lock:
            current = self.get_config(provider)
            data = current.model_dump()
            updates = patch.model_dump(exclude_none=True)
            data.update(updates)
            data["updated_at"] = _now()
            data["updated_by"] = actor
            validated = ProviderConfig.model_validate(data)
            self._state["providers"][provider] = validated.model_dump(mode="json")
            self._append_audit_locked(
                actor,
                "stock.integration.configuration.updated",
                provider,
                {"fields": sorted(updates)},
            )
            self._save()
            return validated

    def append_run(self, run: dict[str, Any]) -> None:
        with self._lock:
            self._state["runs"].insert(0, run)
            del self._state["runs"][100:]
            self._save()

    def runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._state["runs"][:limit])

    def audit(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._state["audit"][:limit])

    def append_audit(
        self,
        actor: str,
        action: str,
        provider: ProviderSlug,
        payload: dict[str, Any],
    ) -> None:
        with self._lock:
            self._append_audit_locked(actor, action, provider, payload)
            self._save()

    def _append_audit_locked(
        self,
        actor: str,
        action: str,
        provider: ProviderSlug,
        payload: dict[str, Any],
    ) -> None:
        self._state["audit"].insert(
            0,
            {
                "id": str(uuid4()),
                "actor": actor,
                "action": action,
                "provider": provider,
                "payload": payload,
                "created_at": _now(),
            },
        )
        del self._state["audit"][200:]


class SecretVault:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _default_secrets_path()
        self._lock = threading.RLock()

    def _fernet(self) -> Fernet:
        key = os.getenv("STOCK_INTEGRATIONS_MASTER_KEY", "").strip()
        if not key:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Cofre indisponivel. Configure STOCK_INTEGRATIONS_MASTER_KEY "
                    "com uma chave Fernet fora do GitHub."
                ),
            )
        try:
            return Fernet(key.encode("utf-8"))
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=503,
                detail="STOCK_INTEGRATIONS_MASTER_KEY nao e uma chave Fernet valida.",
            ) from exc

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        try:
            decrypted = self._fernet().decrypt(self.path.read_bytes())
            raw = json.loads(decrypted.decode("utf-8"))
            if isinstance(raw, dict):
                return {
                    str(provider): {
                        str(name): str(value) for name, value in values.items()
                    }
                    for provider, values in raw.items()
                    if isinstance(values, dict)
                }
        except (OSError, ValueError, json.JSONDecodeError, InvalidToken) as exc:
            raise HTTPException(
                status_code=500,
                detail="Nao foi possivel abrir o cofre de credenciais STOCK.",
            ) from exc
        return {}

    def _save(self, data: dict[str, dict[str, str]]) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        encrypted = self._fernet().encrypt(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "wb",
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            delete=False,
        ) as handle:
            handle.write(encrypted)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, self.path)

    def set(self, provider: ProviderSlug, values: dict[str, str]) -> None:
        with self._lock:
            data = self._load()
            current = data.setdefault(provider, {})
            current.update(values)
            self._save(data)

    def clear(self, provider: ProviderSlug, names: list[str]) -> None:
        with self._lock:
            data = self._load()
            current = data.setdefault(provider, {})
            for name in names:
                current.pop(name, None)
            self._save(data)

    def resolve(
        self,
        provider: ProviderSlug,
        name: str,
        env_name: str | None,
    ) -> str | None:
        if env_name:
            env_value = os.getenv(env_name)
            if env_value:
                return env_value
        try:
            return self._load().get(provider, {}).get(name)
        except HTTPException as exc:
            if exc.status_code == 503:
                return None
            raise

    def status(
        self,
        provider: ProviderSlug,
        config: ProviderConfig,
    ) -> dict[str, bool]:
        manifest = PROVIDER_MANIFESTS[provider]
        fields = set(manifest["secret_env_defaults"]) | set(config.secret_env)
        return {
            field: bool(self.resolve(provider, field, config.secret_env.get(field)))
            for field in sorted(fields)
        }


STORE = IntegrationStore()
VAULT = SecretVault()
CLIENT = httpx.Client(follow_redirects=False)


def _admin_actor(
    x_actor_user_id: str | None,
    x_actor_roles: str | None,
    x_mfa_verified: str | None,
    *,
    require_mfa: bool = False,
) -> str:
    actor = (x_actor_user_id or "").strip()
    roles = {
        role.strip().casefold()
        for role in (x_actor_roles or "").split(",")
        if role.strip()
    }
    if not actor:
        raise HTTPException(status_code=401, detail="Usuario administrador nao identificado.")
    if not roles.intersection({"admin", "owner", "stock_admin", "integration_admin"}):
        raise HTTPException(status_code=403, detail="Permissao administrativa insuficiente.")
    if require_mfa and (x_mfa_verified or "").strip().casefold() != "true":
        raise HTTPException(status_code=403, detail="MFA obrigatorio para alterar credenciais.")
    return actor


def _provider_state(provider: ProviderSlug) -> dict[str, Any]:
    config = STORE.get_config(provider)
    manifest = PROVIDER_MANIFESTS[provider]
    secret_status = VAULT.status(provider, config)
    missing = [
        name
        for name in manifest["required_for_connection"]
        if not secret_status.get(name, False)
    ]
    if provider == "aliexpress" and not config.callback_url:
        missing.append("callback_url")
    return {
        "provider": provider,
        "display_name": manifest["display_name"],
        "docs_url": manifest["docs_url"],
        "auth_kind": manifest["auth_kind"],
        "capabilities": manifest["capabilities"],
        "endpoints": manifest["endpoints"],
        "config": config.model_dump(mode="json"),
        "secret_status": secret_status,
        "missing_requirements": missing,
        "ready_for_connection": config.enabled and not missing,
        "secrets_are_never_returned": True,
    }


def _provider_secret(
    provider: ProviderSlug,
    config: ProviderConfig,
    name: str,
) -> str | None:
    return VAULT.resolve(provider, name, config.secret_env.get(name))


def _cj_access_token(config: ProviderConfig) -> str:
    access_token = _provider_secret("cj_dropshipping", config, "access_token")
    if access_token:
        return access_token
    api_key = _provider_secret("cj_dropshipping", config, "api_key")
    if not api_key:
        raise HTTPException(status_code=409, detail="CJ API Key nao configurada.")
    token_url = (
        config.token_url
        or PROVIDER_MANIFESTS["cj_dropshipping"]["default_token_url"]
    )
    try:
        response = CLIENT.post(
            token_url,
            json={"apiKey": api_key},
            timeout=config.timeout_seconds,
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Falha ao obter token da CJ.") from exc
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"CJ recusou a autenticacao: HTTP {response.status_code}.",
        )
    payload = response.json()
    data = payload.get("data") if isinstance(payload, dict) else None
    token = data.get("accessToken") if isinstance(data, dict) else None
    if not token:
        message = payload.get("message") if isinstance(payload, dict) else None
        raise HTTPException(
            status_code=502,
            detail=message or "CJ nao retornou access token.",
        )
    refresh_token = data.get("refreshToken") if isinstance(data, dict) else None
    if os.getenv("STOCK_INTEGRATIONS_MASTER_KEY"):
        values = {"access_token": str(token)}
        if refresh_token:
            values["refresh_token"] = str(refresh_token)
        VAULT.set("cj_dropshipping", values)
    return str(token)


def _build_aliexpress_authorize_url(config: ProviderConfig) -> str:
    app_key = _provider_secret("aliexpress", config, "app_key")
    if not app_key:
        raise HTTPException(status_code=409, detail="AliExpress App Key nao configurada.")
    if not config.callback_url:
        raise HTTPException(
            status_code=409,
            detail="Callback OAuth do AliExpress nao configurado.",
        )
    base = (
        config.authorization_url
        or PROVIDER_MANIFESTS["aliexpress"]["default_authorization_url"]
    )
    query = urlencode(
        {
            "response_type": "code",
            "force_auth": "true",
            "redirect_uri": config.callback_url,
            "client_id": app_key,
        }
    )
    return f"{base}?{query}"


def _safe_summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"response_type": type(payload).__name__}
    data = payload.get("data")
    summary: dict[str, Any] = {
        "code": payload.get("code"),
        "result": payload.get("result", payload.get("success")),
        "message": payload.get("message"),
        "request_id": payload.get("requestId"),
    }
    if isinstance(data, dict):
        summary["data_fields"] = sorted(data)[:30]
    elif isinstance(data, list):
        summary["item_count"] = len(data)
    return summary


@router.get("/providers")
def list_providers() -> dict[str, Any]:
    return {
        "providers": [
            _provider_state(provider) for provider in PROVIDER_MANIFESTS
        ]
    }


@router.get("/providers/{provider}")
def get_provider(provider: ProviderSlug) -> dict[str, Any]:
    return _provider_state(provider)


@router.get("/readiness")
def readiness() -> dict[str, Any]:
    providers = [_provider_state(provider) for provider in PROVIDER_MANIFESTS]
    return {
        "stock_supplier_integration_ready": all(
            item["ready_for_connection"]
            for item in providers
            if item["config"]["enabled"]
        ),
        "enabled_provider_count": sum(
            1 for item in providers if item["config"]["enabled"]
        ),
        "providers": providers,
        "required_server_settings": [
            "STOCK_INTEGRATIONS_CONFIG_PATH",
            "STOCK_INTEGRATIONS_SECRETS_PATH",
            "STOCK_INTEGRATIONS_MASTER_KEY",
        ],
    }


@router.put("/providers/{provider}")
def update_provider(
    provider: ProviderSlug,
    body: ProviderConfigPatch,
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, Any]:
    actor = _admin_actor(x_actor_user_id, x_actor_roles, x_mfa_verified)
    STORE.patch_config(provider, body, actor)
    return _provider_state(provider)


@router.put("/providers/{provider}/secrets")
def save_provider_secrets(
    provider: ProviderSlug,
    body: ProviderSecretsInput,
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, Any]:
    actor = _admin_actor(
        x_actor_user_id,
        x_actor_roles,
        x_mfa_verified,
        require_mfa=True,
    )
    values = body.non_empty()
    if not values:
        raise HTTPException(
            status_code=422,
            detail="Nenhuma credencial foi informada.",
        )
    allowed = set(PROVIDER_MANIFESTS[provider]["secret_env_defaults"])
    invalid = sorted(set(values) - allowed)
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Credenciais nao suportadas: {', '.join(invalid)}",
        )
    VAULT.set(provider, values)
    STORE.append_audit(
        actor,
        "stock.integration.secrets.updated",
        provider,
        {"fields": sorted(values), "values_logged": False},
    )
    return _provider_state(provider)


@router.delete("/providers/{provider}/secrets")
def clear_provider_secrets(
    provider: ProviderSlug,
    body: SecretClearRequest,
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, Any]:
    actor = _admin_actor(
        x_actor_user_id,
        x_actor_roles,
        x_mfa_verified,
        require_mfa=True,
    )
    VAULT.clear(provider, body.names)
    STORE.append_audit(
        actor,
        "stock.integration.secrets.cleared",
        provider,
        {"fields": sorted(body.names)},
    )
    return _provider_state(provider)


@router.post("/providers/{provider}/test")
def test_provider_connection(
    provider: ProviderSlug,
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, Any]:
    actor = _admin_actor(x_actor_user_id, x_actor_roles, x_mfa_verified)
    config = STORE.get_config(provider)
    state = _provider_state(provider)
    if state["missing_requirements"]:
        raise HTTPException(
            status_code=409,
            detail=(
                "Configuracao incompleta: "
                f"{', '.join(state['missing_requirements'])}."
            ),
        )
    started_at = _now()
    try:
        if provider == "cj_dropshipping":
            token = _cj_access_token(config)
            path = config.connection_test_path or "/api2.0/v1/setting/get"
            response = CLIENT.get(
                f"{config.api_base_url}{path}",
                headers={"CJ-Access-Token": token},
                timeout=config.timeout_seconds,
            )
            result = {
                "status": (
                    "connected" if response.status_code == 200 else "rejected"
                ),
                "http_status": response.status_code,
                "summary": _safe_summary(
                    response.json() if response.content else {}
                ),
            }
        else:
            result = {
                "status": "oauth_ready",
                "authorization_url": _build_aliexpress_authorize_url(config),
                "access_token_configured": bool(
                    _provider_secret("aliexpress", config, "access_token")
                ),
                "message": (
                    "Estrutura OAuth pronta. Conclua a autorizacao do vendedor "
                    "para obter o access token."
                ),
            }
    except (ValueError, httpx.RequestError) as exc:
        result = {"status": "error", "message": str(exc)}
    run = {
        "id": str(uuid4()),
        "provider": provider,
        "kind": "connection_test",
        "status": result["status"],
        "started_at": started_at,
        "completed_at": _now(),
        "actor": actor,
        "result": result,
    }
    STORE.append_run(run)
    STORE.append_audit(
        actor,
        "stock.integration.connection_tested",
        provider,
        {"status": result["status"]},
    )
    return run


@router.get("/providers/aliexpress/authorize-url")
def aliexpress_authorize_url(
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, str]:
    _admin_actor(x_actor_user_id, x_actor_roles, x_mfa_verified)
    return {
        "authorization_url": _build_aliexpress_authorize_url(
            STORE.get_config("aliexpress")
        )
    }


@router.post("/providers/aliexpress/oauth/callback")
def aliexpress_oauth_callback(
    body: OAuthCallbackRequest,
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, Any]:
    actor = _admin_actor(
        x_actor_user_id,
        x_actor_roles,
        x_mfa_verified,
        require_mfa=True,
    )
    config = STORE.get_config("aliexpress")
    app_key = _provider_secret("aliexpress", config, "app_key")
    app_secret = _provider_secret("aliexpress", config, "app_secret")
    if not app_key or not app_secret or not config.callback_url:
        raise HTTPException(
            status_code=409,
            detail="AliExpress OAuth ainda nao esta completamente configurado.",
        )
    token_url = (
        config.token_url
        or PROVIDER_MANIFESTS["aliexpress"]["default_token_url"]
    )
    try:
        response = CLIENT.post(
            token_url,
            json={
                "app_key": app_key,
                "app_secret": app_secret,
                "code": body.code,
                "redirect_uri": config.callback_url,
            },
            timeout=config.timeout_seconds,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Falha no exchange OAuth do AliExpress.",
        ) from exc
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                "AliExpress recusou o exchange OAuth: "
                f"HTTP {response.status_code}."
            ),
        )
    payload = response.json()
    access_token = payload.get("access_token") or payload.get("accessToken")
    refresh_token = payload.get("refresh_token") or payload.get("refreshToken")
    if not access_token:
        raise HTTPException(
            status_code=502,
            detail="AliExpress nao retornou access token.",
        )
    values = {"access_token": str(access_token)}
    if refresh_token:
        values["refresh_token"] = str(refresh_token)
    VAULT.set("aliexpress", values)
    STORE.append_audit(
        actor,
        "stock.integration.oauth.completed",
        "aliexpress",
        {
            "access_token_stored": True,
            "refresh_token_stored": bool(refresh_token),
        },
    )
    return _provider_state("aliexpress")


def _cj_sync_preview(
    config: ProviderConfig,
    body: SyncRequest,
) -> dict[str, Any]:
    token = _cj_access_token(config)
    previews: dict[str, Any] = {}
    endpoints = PROVIDER_MANIFESTS["cj_dropshipping"]["endpoints"]
    for resource in body.resources:
        if resource == "products":
            response = CLIENT.get(
                f"{config.api_base_url}{endpoints['products']}",
                headers={"CJ-Access-Token": token},
                params={
                    "page": 1,
                    "size": body.limit,
                    "keyWord": body.query or "",
                },
                timeout=config.timeout_seconds,
            )
        elif resource == "inventory" and body.product_id:
            response = CLIENT.get(
                f"{config.api_base_url}{endpoints['inventory']}",
                headers={"CJ-Access-Token": token},
                params={"pid": body.product_id},
                timeout=config.timeout_seconds,
            )
        elif resource == "orders":
            response = CLIENT.get(
                f"{config.api_base_url}{endpoints['orders']}",
                headers={"CJ-Access-Token": token},
                params={"pageNum": 1, "pageSize": body.limit},
                timeout=config.timeout_seconds,
            )
        elif resource == "tracking" and body.tracking_number:
            response = CLIENT.get(
                f"{config.api_base_url}{endpoints['tracking']}",
                headers={"CJ-Access-Token": token},
                params={"trackingNumber": body.tracking_number},
                timeout=config.timeout_seconds,
            )
        else:
            previews[resource] = {
                "status": (
                    "input_required"
                    if resource in {"inventory", "tracking"}
                    else "connector_ready"
                ),
                "message": (
                    "Informe o identificador exigido ou execute pelo worker "
                    "agendado."
                ),
            }
            continue
        previews[resource] = {
            "http_status": response.status_code,
            "summary": _safe_summary(
                response.json() if response.content else {}
            ),
        }
    return previews


@router.post("/providers/{provider}/sync")
def sync_provider(
    provider: ProviderSlug,
    body: SyncRequest,
    x_actor_user_id: str | None = Header(
        default=None,
        alias="X-Actor-User-Id",
    ),
    x_actor_roles: str | None = Header(default=None, alias="X-Actor-Roles"),
    x_mfa_verified: str | None = Header(default=None, alias="X-MFA-Verified"),
) -> dict[str, Any]:
    actor = _admin_actor(x_actor_user_id, x_actor_roles, x_mfa_verified)
    config = STORE.get_config(provider)
    state = _provider_state(provider)
    if not config.enabled:
        raise HTTPException(
            status_code=409,
            detail="Ative o provedor antes de sincronizar.",
        )
    if state["missing_requirements"]:
        raise HTTPException(
            status_code=409,
            detail=(
                "Configuracao incompleta: "
                f"{', '.join(state['missing_requirements'])}."
            ),
        )
    unsupported = sorted(
        set(body.resources) - set(PROVIDER_MANIFESTS[provider]["capabilities"])
    )
    if unsupported:
        raise HTTPException(
            status_code=422,
            detail=f"Recursos nao suportados: {', '.join(unsupported)}",
        )
    started_at = _now()
    if body.dry_run:
        result: dict[str, Any] = {
            "execution_mode": "dry_run",
            "resources": body.resources,
            "endpoint_plan": {
                resource: PROVIDER_MANIFESTS[provider]["endpoints"].get(resource)
                for resource in body.resources
            },
            "max_products_per_run": min(
                body.limit,
                config.max_products_per_run,
            ),
        }
        status = "validated"
    elif provider == "cj_dropshipping":
        try:
            result = {
                "execution_mode": "live_preview",
                "preview": _cj_sync_preview(config, body),
                "persisted_to_catalog": False,
                "next_step": (
                    "Worker de importacao deve normalizar e gravar "
                    "catalog_products apos aprovacao."
                ),
            }
            status = "completed"
        except (ValueError, httpx.RequestError) as exc:
            result = {
                "execution_mode": "live_preview",
                "message": str(exc),
            }
            status = "error"
    else:
        result = {
            "execution_mode": "oauth_connector_ready",
            "resources": body.resources,
            "access_token_configured": bool(
                _provider_secret("aliexpress", config, "access_token")
            ),
            "next_step": (
                "Concluir OAuth e configurar os nomes de API liberados no "
                "portal AliExpress."
            ),
        }
        status = "validated"
    run = {
        "id": str(uuid4()),
        "provider": provider,
        "kind": "sync",
        "status": status,
        "dry_run": body.dry_run,
        "resources": body.resources,
        "started_at": started_at,
        "completed_at": _now(),
        "actor": actor,
        "result": result,
    }
    STORE.append_run(run)
    STORE.append_audit(
        actor,
        "stock.integration.sync.requested",
        provider,
        {
            "resources": body.resources,
            "dry_run": body.dry_run,
            "status": status,
        },
    )
    return run


@router.get("/runs")
def integration_runs(limit: int = 50) -> dict[str, Any]:
    return {"runs": STORE.runs(limit=max(1, min(limit, 100)))}


@router.get("/audit")
def integration_audit(limit: int = 100) -> dict[str, Any]:
    return {"audit": STORE.audit(limit=max(1, min(limit, 200)))}


@router.post("/webhooks/{provider}")
async def provider_webhook(
    provider: ProviderSlug,
    request: Request,
) -> dict[str, Any]:
    config = STORE.get_config(provider)
    secret = _provider_secret(provider, config, "webhook_secret")
    if not secret:
        raise HTTPException(
            status_code=409,
            detail="Webhook secret nao configurado.",
        )
    body = await request.body()
    signature = request.headers.get("X-All-in-One-Signature", "")
    expected = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature.removeprefix("sha256="), expected):
        raise HTTPException(
            status_code=401,
            detail="Assinatura de webhook invalida.",
        )
    event = {
        "id": str(uuid4()),
        "provider": provider,
        "kind": "webhook",
        "status": "received",
        "started_at": _now(),
        "completed_at": _now(),
        "actor": "provider-webhook",
        "result": {
            "payload_sha256": hashlib.sha256(body).hexdigest(),
            "content_type": request.headers.get("Content-Type"),
            "payload_logged": False,
        },
    }
    STORE.append_run(event)
    return {"accepted": True, "event_id": event["id"]}
