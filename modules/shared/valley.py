from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import UUID

from fastapi import Body, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .security import (
    Actor,
    actor_from_headers,
    demand_active_business,
    demand_valley_master_stock,
    enforce_essential_plan,
)
from .valley_catalog import (
    build_valley_offers,
    find_valley_offer,
    search_valley_offers,
    valley_business_activities,
    valley_categories,
    valley_facets,
    valley_modules,
)

PEPITA_GRANT_AMOUNTS = {1, 10, 100}
VALLEY_GOLD_ENTRY_TYPES = {"purchase_credit", "pepita_grant_debit", "manual_adjustment"}
VALLEY_GOLD_REFERENCE_TYPES = {"gold_purchase", "pepita_grant", "manual_adjustment"}
STOCK_DISCOUNT_TIERS = (
    {"percent": 10, "pepitas_required": 100},
    {"percent": 20, "pepitas_required": 200},
    {"percent": 50, "pepitas_required": 500},
)
STOCK_GLOBAL_RESOURCES = {
    "suppliers",
    "catalog_products",
    "price_rules",
    "supplier_orders",
}
MARKETPLACE_MERCHANT_RESOURCES = {"stores", "products"}
REVIEW_ELIGIBLE_ORDER_STATUSES = {"delivered", "completed"}


class ValleyPepitaGrant(BaseModel):
    pepitas: int = Field(
        description="Concessao manual permitida: 1, 10 ou 100 Pepitas."
    )
    customer_user_id: UUID
    merchant_gold_ledger_id: str = Field(min_length=3, max_length=120)
    note: str | None = Field(default=None, max_length=280)


class ValleyStockDiscountRequest(BaseModel):
    catalog_product_id: UUID | None = None
    price_brl: Decimal
    user_pepitas_balance: int = Field(ge=0)


class ValleyStockDiscountQuoteRequest(ValleyStockDiscountRequest):
    selected_percent: int


class ValleyAccessRecoveryRequest(BaseModel):
    cpf: str = Field(pattern=r"^\d{11}$")
    device_fingerprint: str = Field(min_length=8, max_length=256)


def decimal_money(value: Any, field: str) -> Decimal:
    try:
        amount = Decimal(str(value))
    except Exception:
        raise HTTPException(
            status_code=422, detail=f"Valor monetario invalido: {field}."
        ) from None
    if amount < 0:
        raise HTTPException(
            status_code=422, detail=f"Valor monetario invalido: {field}."
        )
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def stock_discount_options(user_pepitas_balance: int) -> list[dict[str, int]]:
    return [
        tier
        for tier in STOCK_DISCOUNT_TIERS
        if user_pepitas_balance >= tier["pepitas_required"]
    ]


def validate_valley_resource_policy(
    module_name: str, resource_type: str, payload: dict[str, Any], actor: Actor
) -> None:
    if module_name == "stock" and resource_type in STOCK_GLOBAL_RESOURCES:
        demand_valley_master_stock(actor)
    if module_name == "business" and resource_type in {"companies", "branches"}:
        enforce_essential_plan(actor, payload)
    if module_name == "marketplace" and resource_type in MARKETPLACE_MERCHANT_RESOURCES:
        demand_active_business(
            actor, "gerenciar estoque fisico local no Valley Business"
        )
        enforce_essential_plan(actor, payload)
        if payload.get("inventory_source") in {
            "global_stock",
            "dropshipping",
            "supplier_import",
        }:
            raise HTTPException(
                status_code=403,
                detail="Valley Business gerencia somente estoque fisico local do proprio lojista.",
            )
        if (
            resource_type == "products"
            and payload.get("stock_location_type") != "local_physical"
        ):
            raise HTTPException(
                status_code=422,
                detail="Produto Marketplace exige stock_location_type=local_physical.",
            )
        if any(
            key in payload
            for key in ("amazon_asin", "aliexpress_item_id", "cj_product_id")
        ):
            raise HTTPException(
                status_code=403,
                detail="APIs de importacao global pertencem apenas ao Modulo Stock corporativo Valley.",
            )


def validate_valley_gold_ledger_payload(payload: dict[str, Any]) -> None:
    entry_type = payload.get("entry_type")
    if entry_type not in VALLEY_GOLD_ENTRY_TYPES:
        raise HTTPException(
            status_code=422, detail="Tipo de lancamento Gold Valley invalido."
        )
    if payload.get("reference_type") not in VALLEY_GOLD_REFERENCE_TYPES:
        raise HTTPException(status_code=422, detail="Referencia Gold Valley invalida.")
    try:
        amount = int(payload.get("amount_gold_delta"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422, detail="amount_gold_delta deve ser inteiro nao nulo."
        ) from None
    if amount == 0:
        raise HTTPException(
            status_code=422, detail="amount_gold_delta nao pode ser zero."
        )
    if entry_type == "purchase_credit" and amount <= 0:
        raise HTTPException(
            status_code=422, detail="Compra de Gold deve registrar credito positivo."
        )
    if entry_type == "pepita_grant_debit" and amount >= 0:
        raise HTTPException(
            status_code=422,
            detail="Uso de Gold em Pepitas deve registrar debito negativo.",
        )
    if entry_type == "pepita_grant_debit" and not payload.get("reference_id"):
        raise HTTPException(
            status_code=422,
            detail="Debito Gold por Pepitas exige reference_id da concessao.",
        )
    if payload.get("auto_grant_pepitas"):
        raise HTTPException(
            status_code=422,
            detail="Gold nao concede Pepitas automaticamente; concessao continua manual pelo lojista.",
        )


def register_valley_routes(
    app: FastAPI,
    module_name: str,
    store: Any,
    fetch: Callable[[str, UUID], dict[str, Any]],
) -> None:
    @app.get("/valley/catalog/modules")
    def valley_catalog_modules() -> list[dict[str, Any]]:
        return valley_modules()

    @app.get("/valley/catalog/categories")
    def valley_catalog_categories() -> list[dict[str, Any]]:
        return valley_categories()

    @app.get("/valley/catalog/business-activities")
    def valley_catalog_business_activities() -> list[dict[str, Any]]:
        return valley_business_activities()

    @app.get("/valley/catalog/facets")
    def valley_catalog_facets() -> dict[str, list[dict[str, Any]]]:
        return valley_facets(build_valley_offers(module_name, store))

    @app.get("/valley/catalog")
    def valley_catalog_home(
        q: str | None = None,
        category: str | None = None,
        offer_type: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        company_type: str | None = None,
        company_category: str | None = None,
        business_activity: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        availability: str | None = None,
        verified_only: bool = False,
    ) -> list[dict[str, Any]]:
        return search_valley_offers(
            build_valley_offers(module_name, store),
            q=q,
            category=category,
            offer_type=offer_type,
            lat=lat,
            lng=lng,
            company_type=company_type,
            company_category=company_category,
            business_activity=business_activity,
            price_min=price_min,
            price_max=price_max,
            availability=availability,
            verified_only=verified_only,
        )

    @app.get("/valley/catalog/offers")
    def valley_catalog_offers() -> list[dict[str, Any]]:
        return build_valley_offers(module_name, store)

    @app.get("/valley/catalog/offers/{offer_id}")
    def valley_catalog_offer_detail(offer_id: str) -> dict[str, Any]:
        offer = find_valley_offer(build_valley_offers(module_name, store), offer_id)
        if offer is None:
            raise HTTPException(
                status_code=404, detail="Oferta nao encontrada no catalogo Valley."
            )
        return offer

    @app.get("/valley/catalog/search")
    def valley_catalog_search(
        q: str | None = None,
        category: str | None = None,
        offer_type: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        company_type: str | None = None,
        company_category: str | None = None,
        business_activity: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        availability: str | None = None,
        verified_only: bool = False,
    ) -> list[dict[str, Any]]:
        return search_valley_offers(
            build_valley_offers(module_name, store),
            q=q,
            category=category,
            offer_type=offer_type,
            lat=lat,
            lng=lng,
            company_type=company_type,
            company_category=company_category,
            business_activity=business_activity,
            price_min=price_min,
            price_max=price_max,
            availability=availability,
            verified_only=verified_only,
        )

    if module_name == "identity":

        @app.post("/valley/access-recovery", status_code=202)
        def request_access_recovery(
            body: ValleyAccessRecoveryRequest = Body(...),
        ) -> dict[str, str]:
            user = next(
                (
                    item
                    for item in store.list("users")
                    if str(item.get("payload", {}).get("document_cpf") or item.get("payload", {}).get("cpf_document") or "") == body.cpf
                ),
                None,
            )
            if user is not None and user.get("status") != "BLOCKED":
                user_id = str(user["id"])
                store.create(
                    "identity_verifications",
                    user_id,
                    None,
                    "PROCESSING",
                    {
                        "verification_type": "access_recovery",
                        "requested_at": datetime.now(UTC).isoformat(),
                        "device_fingerprint_hash": hashlib.sha256(body.device_fingerprint.encode("utf-8")).hexdigest(),
                        "delivery_policy": "registered_contact_only",
                        "account_disclosure": "suppressed",
                    },
                    user_id,
                    (),
                    "identity.access_recovery.requested",
                    None,
                )
            return {
                "status": "accepted",
                "message": "Se houver uma conta elegivel, as instrucoes serao enviadas ao canal seguro cadastrado.",
            }

    if module_name == "marketplace":

        @app.get("/valley/feed/review-eligibility")
        def feed_review_eligibility(
            actor: Actor = Depends(actor_from_headers),
        ) -> list[dict[str, Any]]:
            eligible: list[dict[str, Any]] = []
            for order in store.list("orders", str(actor.user_id)):
                status = str(order.get("status") or "").casefold()
                if status not in REVIEW_ELIGIBLE_ORDER_STATUSES:
                    continue
                payload = order.get("payload") if isinstance(order.get("payload"), dict) else {}
                eligible.append(
                    {
                        "id": str(order.get("id") or ""),
                        "title": str(payload.get("offer_title") or payload.get("title") or ""),
                        "status": status,
                        "offer_id": payload.get("offer_id") or payload.get("source_offer_id"),
                        "source_entity_id": payload.get("source_entity_id") or payload.get("product_id") or payload.get("catalog_product_id"),
                        "source_module": payload.get("source_module") or "marketplace",
                        "can_review": True,
                    }
                )
            return eligible

        @app.post("/valley/orders/{order_id}/pepitas/grants", status_code=201)
        def grant_pepitas(
            order_id: UUID,
            body: ValleyPepitaGrant = Body(...),
            actor: Actor = Depends(actor_from_headers),
            x_idempotency_key: str | None = Header(
                default=None, alias="X-Idempotency-Key"
            ),
        ) -> dict[str, Any]:
            demand_active_business(actor, "conceder Pepitas manualmente")
            if body.pepitas not in PEPITA_GRANT_AMOUNTS:
                raise HTTPException(
                    status_code=422,
                    detail="Concessao manual aceita somente 1, 10 ou 100 Pepitas.",
                )
            if not x_idempotency_key:
                raise HTTPException(
                    status_code=422,
                    detail="X-Idempotency-Key obrigatorio para concessao de Pepitas.",
                )
            order = fetch("orders", order_id)
            if order["status"] not in {"paid", "delivered", "completed"}:
                raise HTTPException(
                    status_code=409,
                    detail="Pepitas somente podem ser concedidas apos venda bem-sucedida.",
                )
            if actor.business_id and str(order.get("entity_id")) not in {
                "None",
                str(actor.business_id),
            }:
                raise HTTPException(
                    status_code=403,
                    detail="Lojista nao autorizado para pedido de outra empresa.",
                )
            payload = {
                "order_id": str(order_id),
                "customer_user_id": str(body.customer_user_id),
                "merchant_business_id": str(actor.business_id)
                if actor.business_id
                else None,
                "merchant_actor_user_id": str(actor.user_id),
                "pepitas": body.pepitas,
                "merchant_gold_ledger_id": body.merchant_gold_ledger_id,
                "grant_mode": "merchant_manual_free_will",
                "note": body.note,
            }
            return store.create(
                "pepita_grants",
                str(body.customer_user_id),
                str(actor.business_id) if actor.business_id else None,
                "posted",
                payload,
                str(actor.user_id),
                (),
                "valley.pepitas.granted",
                x_idempotency_key,
            )

    if module_name == "stock":

        @app.post("/valley/checkout/discount-options")
        def valley_stock_discount_options(
            body: ValleyStockDiscountRequest = Body(...),
        ) -> dict[str, Any]:
            price = decimal_money(body.price_brl, "price_brl")
            options = []
            for tier in stock_discount_options(body.user_pepitas_balance):
                discount = (price * Decimal(tier["percent"]) / Decimal(100)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                options.append(
                    {
                        "percent": tier["percent"],
                        "pepitas_required": tier["pepitas_required"],
                        "discount_brl": str(discount),
                        "final_price_brl": str(
                            (price - discount).quantize(
                                Decimal("0.01"), rounding=ROUND_HALF_UP
                            )
                        ),
                    }
                )
            return {
                "catalog_product_id": str(body.catalog_product_id)
                if body.catalog_product_id
                else None,
                "original_price_brl": str(price),
                "available_discount_options": options,
                "hidden_unavailable_options": len(STOCK_DISCOUNT_TIERS) - len(options),
                "message": "Faixas maiores aparecem como premio quando houver saldo suficiente de Pepitas.",
            }

        @app.post("/valley/checkout/discount-quotes", status_code=201)
        def valley_stock_discount_quote(
            body: ValleyStockDiscountQuoteRequest = Body(...),
            actor: Actor = Depends(actor_from_headers),
            x_idempotency_key: str | None = Header(
                default=None, alias="X-Idempotency-Key"
            ),
        ) -> dict[str, Any]:
            if not x_idempotency_key:
                raise HTTPException(
                    status_code=422,
                    detail="X-Idempotency-Key obrigatorio para cotacao transacional.",
                )
            available = {
                tier["percent"]: tier
                for tier in stock_discount_options(body.user_pepitas_balance)
            }
            tier = available.get(body.selected_percent)
            if tier is None:
                raise HTTPException(
                    status_code=403,
                    detail="Faixa de desconto indisponivel para o saldo atual de Pepitas.",
                )
            price = decimal_money(body.price_brl, "price_brl")
            discount = (price * Decimal(tier["percent"]) / Decimal(100)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            payload = {
                "catalog_product_id": str(body.catalog_product_id)
                if body.catalog_product_id
                else "stock-checkout",
                "selected_percent": tier["percent"],
                "pepitas_required": tier["pepitas_required"],
                "original_price_brl": str(price),
                "discount_brl": str(discount),
                "final_price_brl": str(
                    (price - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                ),
                "visibility_rule": "BR-STO-009",
            }
            return store.create(
                "discount_quotes",
                str(actor.user_id),
                None,
                "quoted",
                payload,
                str(actor.user_id),
                (),
                "valley.stock.discount.quoted",
                x_idempotency_key,
            )
