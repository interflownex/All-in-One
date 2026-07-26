from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "config" / "module_catalog.json"

OFFER_TYPES = {"food", "product", "service"}
PUBLISHABLE_STATUSES = {"approved", "published", "active", "available"}
VISIBLE_PUBLICATION_STATUSES = {"approved", "published"}
REGULATED_MODULES = {"health", "legal", "finance", "document"}
OFFER_TYPE_ALIASES = {
    "alimento": "food",
    "comida": "food",
    "food": "food",
    "produto": "product",
    "product": "product",
    "servico": "service",
    "serviço": "service",
    "service": "service",
}
LOCAL_AREAS = {"local", "regional"}
GLOBAL_AREAS = {"online", "national"}

COMPANY_TYPE_ALIASES = {
    "pf_profissional": "Profissional autonomo",
    "pf_vendedor": "Vendedor pessoa fisica",
    "mei": "MEI",
    "microempresa": "Microempresa",
    "pequena_empresa": "Pequena empresa",
    "media_empresa": "Media empresa",
    "grande_empresa": "Grande empresa",
    "franquia": "Franquia",
    "instituicao": "Instituicao",
    "parceiro_integrado": "Parceiro integrado",
}
OFFER_TYPE_LABELS = {
    "food": "Alimento",
    "product": "Produto",
    "service": "Servico",
}

BUSINESS_ACTIVITY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "alimentacao": {
        "name": "Alimentacao",
        "parent_category": "Comercio",
        "label_for_consumer": "Restaurantes e mercados",
        "allowed_offer_types": ("food", "product"),
        "requires_compliance_review": False,
    },
    "varejo": {
        "name": "Varejo",
        "parent_category": "Comercio",
        "label_for_consumer": "Produtos e lojas",
        "allowed_offer_types": ("product",),
        "requires_compliance_review": False,
    },
    "saude": {
        "name": "Saude",
        "parent_category": "Saude",
        "label_for_consumer": "Saude e bem-estar",
        "allowed_offer_types": ("service",),
        "requires_compliance_review": True,
    },
    "servicos_domesticos": {
        "name": "Servicos domesticos",
        "parent_category": "Servicos",
        "label_for_consumer": "Casa e manutencao",
        "allowed_offer_types": ("service", "product"),
        "requires_compliance_review": False,
    },
    "juridico": {
        "name": "Juridico",
        "parent_category": "Juridico",
        "label_for_consumer": "Advogados e documentos",
        "allowed_offer_types": ("service",),
        "requires_compliance_review": True,
    },
    "educacao": {
        "name": "Educacao",
        "parent_category": "Educacao",
        "label_for_consumer": "Cursos e aulas",
        "allowed_offer_types": ("product", "service"),
        "requires_compliance_review": False,
    },
    "logistica": {
        "name": "Logistica",
        "parent_category": "Logistica",
        "label_for_consumer": "Entregas e transportes",
        "allowed_offer_types": ("service",),
        "requires_compliance_review": False,
    },
    "imobiliario": {
        "name": "Imobiliario",
        "parent_category": "Imobiliario",
        "label_for_consumer": "Imoveis e condominio",
        "allowed_offer_types": ("service", "product"),
        "requires_compliance_review": False,
    },
    "empregos": {
        "name": "Empregos",
        "parent_category": "RH e empregos",
        "label_for_consumer": "Vagas e carreira",
        "allowed_offer_types": ("service",),
        "requires_compliance_review": False,
    },
    "financeiro": {
        "name": "Financeiro",
        "parent_category": "Financeiro",
        "label_for_consumer": "Pagamentos e credito",
        "allowed_offer_types": ("service", "product"),
        "requires_compliance_review": True,
    },
    "tecnologia": {
        "name": "Tecnologia",
        "parent_category": "Tecnologia",
        "label_for_consumer": "Tecnologia e automacao",
        "allowed_offer_types": ("service",),
        "requires_compliance_review": False,
    },
}

CATEGORY_DEFINITIONS: dict[str, dict[str, Any]] = {
    "Comida e Mercado": {
        "offer_types": ("food", "product"),
        "modules": ("delivery", "marketplace", "stock"),
        "keywords": (
            "food",
            "alimento",
            "comida",
            "restaurante",
            "marmita",
            "mercado",
            "delivery",
        ),
    },
    "Compras e Produtos": {
        "offer_types": ("product",),
        "modules": ("marketplace", "stock"),
        "keywords": ("produto", "catalogo", "loja", "assinatura", "curso", "digital"),
    },
    "Saude e Bem-estar": {
        "offer_types": ("service",),
        "modules": ("health", "services"),
        "keywords": (
            "saude",
            "medico",
            "medicina",
            "psicologo",
            "dentista",
            "consulta",
            "telemedicina",
        ),
    },
    "Casa, Reparos e Imoveis": {
        "offer_types": ("service", "product"),
        "modules": ("services", "property", "marketplace"),
        "keywords": (
            "reparo",
            "eletricista",
            "pedreiro",
            "marceneiro",
            "imovel",
            "manutencao",
            "casa",
        ),
    },
    "Mobilidade, Entregas e Logistica": {
        "offer_types": ("service",),
        "modules": ("mobility", "delivery", "riders", "tms"),
        "keywords": ("corrida", "entrega", "frete", "transporte", "logistica", "rider"),
    },
    "Negocios e Profissionais": {
        "offer_types": ("service",),
        "modules": ("legal", "erp", "crm", "bi", "bpm", "document", "hr", "jobs"),
        "keywords": (
            "advogado",
            "contador",
            "recrutamento",
            "consultoria",
            "documento",
            "profissional",
        ),
    },
    "Beneficios, Wallet e Recompensas": {
        "offer_types": ("service", "product"),
        "modules": ("finance", "marketplace", "stock"),
        "keywords": (
            "pepitas",
            "gold",
            "wallet",
            "desconto",
            "beneficio",
            "fidelidade",
            "recompensa",
        ),
    },
    "Tecnologia, Seguranca e IA": {
        "offer_types": ("service",),
        "modules": ("ai_core", "api_hub", "permissions"),
        "keywords": (
            "camera",
            "ia",
            "api",
            "integracao",
            "permissao",
            "seguranca",
            "automacao",
        ),
    },
}

RESOURCE_OFFER_TYPES = {
    "catalog_offers": "service",
    "catalog_products": "product",
    "products": "product",
    "providers": "service",
    "service_contracts": "service",
    "delivery_requests": "food",
    "rides": "service",
    "tickets": "service",
    "job_postings": "service",
    "properties": "service",
    "appointments": "service",
    "valley_gold_ledger_entries": "service",
    "discount_quotes": "product",
}

PUBLIC_RESOURCE_TYPES = {
    "business": ("catalog_offers",),
    "marketplace": ("products",),
    "stock": ("catalog_products", "discount_quotes"),
    "services": ("providers", "service_contracts"),
    "health": ("appointments",),
    "delivery": ("delivery_requests",),
    "mobility": ("rides", "tickets"),
    "jobs": ("job_postings",),
    "property": ("properties",),
    "finance": ("valley_gold_ledger_entries",),
}


def load_module_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def valley_categories() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "offer_types": list(definition["offer_types"]),
            "source_modules": list(definition["modules"]),
            "keywords": list(definition["keywords"]),
        }
        for name, definition in CATEGORY_DEFINITIONS.items()
    ]


def valley_business_activities() -> list[dict[str, Any]]:
    return [
        {"business_activity_id": activity_id, **definition}
        for activity_id, definition in BUSINESS_ACTIVITY_DEFINITIONS.items()
    ]


def valley_facets(offers: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "offer_types": counted_facet(
            offers,
            "offer_type",
            lambda value: OFFER_TYPE_LABELS.get(str(value), str(value).title()),
        ),
        "consumer_categories": counted_facet(offers, "consumer_category", str),
        "company_types": counted_facet(offers, "company_type", company_type_label),
        "company_categories": counted_facet(offers, "company_category", str),
        "business_activities": counted_facet(
            offers, "business_activity_id", business_activity_label
        ),
    }


def valley_modules() -> list[dict[str, Any]]:
    catalog = load_module_catalog()
    return [
        {
            "source_module": module["slug"],
            "technical_title": module["title"],
            "consumer_category": infer_category(
                module["slug"], "records", module["title"], module["description"]
            ),
            "consumer_title": friendly_module_title(module["slug"], module["title"]),
            "description": module["description"],
            "availability_status": "coming_soon",
        }
        for module in catalog["modules"]
    ]


def build_valley_offers(
    module_name: str, store: Any | None = None
) -> list[dict[str, Any]]:
    offers = module_fallback_offers()
    if store is None:
        return offers
    for resource_type in PUBLIC_RESOURCE_TYPES.get(module_name, ()):
        try:
            rows = store.list(resource_type, None)
        except Exception:
            continue
        for row in rows:
            offer = offer_from_resource(module_name, resource_type, row)
            if offer:
                offers.append(offer)
    return deduplicate_offers(offers)


def module_fallback_offers() -> list[dict[str, Any]]:
    catalog = load_module_catalog()
    return [
        {
            "offer_id": f"module:{module['slug']}",
            "offer_type": infer_offer_type(
                module["slug"], "records", module["title"], module["description"]
            ),
            "consumer_category": infer_category(
                module["slug"], "records", module["title"], module["description"]
            ),
            "title": friendly_module_title(module["slug"], module["title"]),
            "description": module["description"],
            "source_module": module["slug"],
            "source_resource_type": "module",
            "availability_status": "coming_soon",
            "price_brl": None,
            "benefits": [],
            "rewards": [],
            "service_origin": None,
            "service_radius_km": None,
            "distance_km": None,
            "region_label": "Disponibilidade em expansao",
            "service_area": "national",
            "consumer_action": "coming_soon",
            "primary_action_label": "Em breve",
            "media": [],
            "source_entity_id": None,
            "business_id": None,
            "seller_user_id": None,
            "short_description": short_description(
                module["description"],
                friendly_module_title(module["slug"], module["title"]),
            ),
            "long_description": module["description"],
            "consumer_friendly_label": friendly_module_title(
                module["slug"], module["title"]
            ),
            "company_type": "parceiro_integrado",
            "company_type_label": COMPANY_TYPE_ALIASES["parceiro_integrado"],
            "company_category": company_category_for(module["slug"], None),
            "business_activity_id": business_activity_for(
                module["slug"], "records", module["title"], module["description"]
            ),
            "business_activity_label": business_activity_label(
                business_activity_for(
                    module["slug"], "records", module["title"], module["description"]
                )
            ),
            "category_id": slugify(
                infer_category(
                    module["slug"], "records", module["title"], module["description"]
                )
            ),
            "price_type": "sob_consulta",
            "price_amount": None,
            "currency": "BRL",
            "availability_type": "sob_consulta",
            "stock_quantity": None,
            "service_duration_minutes": None,
            "attributes": {},
            "requirements": [],
            "compliance_status": "not_required",
            "publication_status": "coming_soon",
            "publish_to_valley": False,
            "visible_to_consumer": True,
            "ranking_score": 0,
            "provider_label": "All-in-One",
            "verified_seller": False,
        }
        for module in catalog["modules"]
    ]


def offer_from_resource(
    module_name: str, resource_type: str, row: dict[str, Any]
) -> dict[str, Any] | None:
    payload = row.get("payload") or {}
    if not publishable_for_valley(module_name, row, payload):
        return None
    source_module = public_source_module(module_name, payload)
    source_resource_type = public_source_resource_type(resource_type, payload)
    title = first_text(
        payload,
        (
            "public_title",
            "name",
            "title",
            "headline",
            "category",
            "service_type",
            "route_code",
            "property_type",
        ),
        fallback=friendly_module_title(module_name, module_name),
    )
    description = first_text(
        payload, ("public_description", "description", "summary"), fallback=title
    )
    offer_type = normalize_offer_type(payload.get("offer_type")) or infer_offer_type(
        source_module, source_resource_type, title, description
    )
    consumer_category = str(
        payload.get("consumer_category")
        or infer_category(source_module, source_resource_type, title, description)
    )
    service_area = str(
        payload.get("service_area")
        or default_service_area(source_module, source_resource_type)
    ).casefold()
    origin = public_origin(payload)
    radius = number_or_none(payload.get("service_radius_km"))
    business_activity_id = str(
        payload.get("business_activity_id")
        or business_activity_for(
            source_module, source_resource_type, title, description
        )
    )
    action = consumer_action_for(source_module, source_resource_type, payload)
    price_amount = price_for(payload)
    company_type = str(payload.get("company_type") or "microempresa")
    activity_label = business_activity_label(business_activity_id)
    type_label = OFFER_TYPE_LABELS.get(offer_type, offer_type.title())
    category_label = str(
        payload.get("company_category")
        or company_category_for(source_module, business_activity_id)
    )
    return {
        "offer_id": f"{module_name}:{resource_type}:{row['id']}",
        "source_entity_id": str(row["id"]),
        "business_id": str(
            row.get("entity_id")
            or payload.get("business_id")
            or payload.get("company_id")
            or ""
        ),
        "seller_user_id": str(
            row.get("user_id") or payload.get("seller_user_id") or ""
        ),
        "offer_type": offer_type,
        "offer_type_label": type_label,
        "consumer_category": consumer_category,
        "title": title,
        "description": description,
        "short_description": short_description(description, title),
        "long_description": str(payload.get("long_description") or description),
        "consumer_friendly_label": str(payload.get("consumer_friendly_label") or title),
        "source_module": source_module,
        "source_resource_type": source_resource_type,
        "configured_in_module": module_name,
        "configured_resource_type": resource_type,
        "availability_status": availability_for(row.get("status")),
        "price_brl": price_amount,
        "price_type": str(
            payload.get("price_type") or default_price_type(price_amount)
        ),
        "price_amount": price_amount,
        "currency": str(payload.get("currency") or "BRL"),
        "benefits": list_or_empty(payload.get("benefits")),
        "rewards": list_or_empty(payload.get("rewards")),
        "service_origin": origin,
        "service_radius_km": radius,
        "distance_km": None,
        "region_label": str(
            payload.get("region_label") or default_region_label(service_area)
        ),
        "service_area": service_area,
        "consumer_action": action,
        "primary_action_label": action_label_for(action, business_activity_id),
        "media": list_or_empty(payload.get("media")),
        "company_type": company_type,
        "company_type_label": company_type_label(company_type),
        "company_category": category_label,
        "business_activity_id": business_activity_id,
        "business_activity_label": activity_label,
        "business_activity_consumer_label": activity_label,
        "seller_context_label": f"{company_type_label(company_type)} em {activity_label}",
        "consumer_filter_text": f"{type_label} em {consumer_category} - {activity_label}",
        "category_id": str(payload.get("category_id") or slugify(consumer_category)),
        "availability_type": str(
            payload.get("availability_type")
            or default_availability_type(source_module, source_resource_type)
        ),
        "stock_quantity": integer_or_none(payload.get("stock_quantity")),
        "service_duration_minutes": integer_or_none(
            payload.get("service_duration_minutes")
        ),
        "attributes": dict_or_empty(payload.get("attributes")),
        "requirements": list_or_empty(payload.get("requirements")),
        "compliance_status": default_compliance_status(source_module, payload),
        "publication_status": publication_status_for(row, payload),
        "publish_to_valley": True,
        "visible_to_consumer": payload.get("visible_to_consumer") is not False,
        "ranking_score": number_or_none(payload.get("ranking_score")) or 0,
        "provider_label": str(
            payload.get("provider_label")
            or payload.get("store_name")
            or "Prestador verificado"
        ),
        "verified_seller": bool(
            payload.get("verified_seller") or payload.get("identity_validated")
        ),
    }


def search_valley_offers(
    offers: list[dict[str, Any]],
    *,
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
    normalized_type = normalize_offer_type(offer_type) if offer_type else None
    terms = (q or "").strip().casefold()
    selected_category = (category or "").strip().casefold()
    results: list[dict[str, Any]] = []
    for offer in offers:
        if normalized_type and offer["offer_type"] != normalized_type:
            continue
        if (
            selected_category
            and selected_category not in str(offer["consumer_category"]).casefold()
        ):
            continue
        if (
            company_type
            and str(company_type).casefold()
            != str(offer.get("company_type")).casefold()
        ):
            continue
        if (
            company_category
            and str(company_category).casefold()
            not in str(offer.get("company_category", "")).casefold()
        ):
            continue
        if business_activity:
            selected_activity = str(business_activity).casefold()
            if selected_activity not in {
                str(offer.get("business_activity_id", "")).casefold(),
                str(offer.get("business_activity_label", "")).casefold(),
            }:
                continue
        if (
            availability
            and str(availability).casefold()
            != str(offer.get("availability_status")).casefold()
        ):
            continue
        if verified_only and not offer.get("verified_seller"):
            continue
        price_value = number_or_none(offer.get("price_amount"))
        if price_min is not None and (price_value is None or price_value < price_min):
            continue
        if price_max is not None and (price_value is None or price_value > price_max):
            continue
        if terms:
            material = " ".join(
                str(offer.get(key) or "")
                for key in (
                    "title",
                    "description",
                    "consumer_category",
                    "source_module",
                    "source_resource_type",
                    "company_type_label",
                    "company_category",
                    "business_activity_label",
                    "seller_context_label",
                    "consumer_filter_text",
                )
            ).casefold()
            if terms not in material:
                continue
        localized = with_distance(offer, lat, lng)
        if lat is not None and lng is not None and not visible_for_location(localized):
            continue
        results.append(localized)
    return sorted(results, key=offer_sort_key)


def find_valley_offer(
    offers: list[dict[str, Any]], offer_id: str
) -> dict[str, Any] | None:
    for offer in offers:
        if offer.get("offer_id") == offer_id:
            return offer
    return None


def with_distance(
    offer: dict[str, Any], lat: float | None, lng: float | None
) -> dict[str, Any]:
    copy = dict(offer)
    if lat is None or lng is None or not offer.get("service_origin"):
        return copy
    origin = offer["service_origin"]
    distance = haversine_km(
        lat, lng, float(origin["latitude"]), float(origin["longitude"])
    )
    copy["distance_km"] = round(distance, 3)
    radius = offer.get("service_radius_km")
    if (
        offer.get("service_area") in LOCAL_AREAS
        and radius is not None
        and distance > float(radius)
    ):
        copy["availability_status"] = "unavailable_for_location"
    return copy


def visible_for_location(offer: dict[str, Any]) -> bool:
    if offer.get("availability_status") == "coming_soon":
        return True
    if offer.get("service_area") in GLOBAL_AREAS:
        return True
    if offer.get("service_area") not in LOCAL_AREAS:
        return True
    if offer.get("availability_status") == "unavailable_for_location":
        return False
    return (
        offer.get("distance_km") is not None
        and offer.get("service_radius_km") is not None
    )


def offer_sort_key(offer: dict[str, Any]) -> tuple[int, float, str]:
    area = offer.get("service_area")
    status = offer.get("availability_status")
    if status in {"available", "limited"} and offer.get("distance_km") is not None:
        tier = 0
    elif area in GLOBAL_AREAS:
        tier = 1
    elif status == "coming_soon":
        tier = 3
    else:
        tier = 2
    distance = (
        float(offer["distance_km"])
        if offer.get("distance_km") is not None
        else 999999.0
    )
    return (tier, distance, str(offer.get("title", "")))


def haversine_km(lat_a: float, lng_a: float, lat_b: float, lng_b: float) -> float:
    earth_km = 6371.0
    delta_lat = math.radians(lat_b - lat_a)
    delta_lng = math.radians(lng_b - lng_a)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(math.radians(lat_a))
        * math.cos(math.radians(lat_b))
        * math.sin(delta_lng / 2) ** 2
    )
    return earth_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def infer_offer_type(
    module_name: str, resource_type: str, title: str, description: str
) -> str:
    material = f"{module_name} {resource_type} {title} {description}".casefold()
    if any(
        keyword in material
        for keyword in CATEGORY_DEFINITIONS["Comida e Mercado"]["keywords"]
    ):
        return "food"
    if RESOURCE_OFFER_TYPES.get(resource_type):
        return RESOURCE_OFFER_TYPES[resource_type]
    if module_name in {"marketplace", "stock"}:
        return "product"
    return "service"


def infer_category(
    module_name: str, resource_type: str, title: str, description: str
) -> str:
    material = f"{module_name} {resource_type} {title} {description}".casefold()
    for name, definition in CATEGORY_DEFINITIONS.items():
        if module_name in definition["modules"]:
            return name
        if any(keyword in material for keyword in definition["keywords"]):
            return name
    return "Negocios e Profissionais"


def normalize_offer_type(value: Any) -> str | None:
    if value is None:
        return None
    return OFFER_TYPE_ALIASES.get(str(value).strip().casefold())


def public_source_module(module_name: str, payload: dict[str, Any]) -> str:
    candidate = str(payload.get("source_module") or module_name).strip().casefold()
    modules = {module["slug"] for module in load_module_catalog()["modules"]}
    return candidate if candidate in modules else module_name


def public_source_resource_type(resource_type: str, payload: dict[str, Any]) -> str:
    candidate = str(payload.get("source_resource_type") or resource_type).strip()
    return candidate or resource_type


def public_origin(payload: dict[str, Any]) -> dict[str, float] | None:
    origin = payload.get("service_origin")
    if isinstance(origin, dict):
        latitude = number_or_none(origin.get("latitude"))
        longitude = number_or_none(origin.get("longitude"))
    else:
        latitude = number_or_none(payload.get("latitude"))
        longitude = number_or_none(payload.get("longitude"))
    if latitude is None or longitude is None:
        return None
    return {"latitude": latitude, "longitude": longitude}


def number_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def integer_or_none(value: Any) -> int | None:
    number = number_or_none(value)
    if number is None:
        return None
    return int(number)


def price_for(payload: dict[str, Any]) -> str | None:
    for key in (
        "price_brl",
        "list_price_brl",
        "visit_price_brl",
        "fare_brl",
        "amount_brl",
        "contracted_price_brl",
    ):
        if payload.get(key) not in (None, ""):
            return str(payload[key])
    return None


def default_price_type(price_amount: str | None) -> str:
    return "fixed" if price_amount not in (None, "") else "sob_orcamento"


def first_text(payload: dict[str, Any], keys: tuple[str, ...], fallback: str) -> str:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return fallback


def list_or_empty(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def dict_or_empty(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def availability_for(status: Any) -> str:
    normalized = str(status or "").casefold()
    if normalized in {
        "active",
        "approved",
        "published",
        "available",
        "posted",
        "quoted",
        "completed",
    }:
        return "available"
    if normalized in {
        "draft",
        "pending_validation",
        "pending_review",
        "created",
        "requested",
    }:
        return "limited"
    if normalized in {"cancelled", "rejected", "blocked", "suspended", "archived"}:
        return "unavailable"
    return "limited"


def publication_status_for(row: dict[str, Any], payload: dict[str, Any]) -> str:
    explicit = payload.get("publication_status")
    if explicit:
        return str(explicit).casefold()
    status = str(row.get("status") or "").casefold()
    if status == "published":
        return "published"
    if status in PUBLISHABLE_STATUSES:
        return "approved"
    if status in {"rejected", "cancelled", "blocked", "suspended"}:
        return "rejected"
    if status in {
        "draft",
        "pending_review",
        "pending_validation",
        "created",
        "requested",
    }:
        return "draft"
    return "pending_review"


def publishable_for_valley(
    module_name: str, row: dict[str, Any], payload: dict[str, Any]
) -> bool:
    if payload.get("publish_to_valley") is not True:
        return False
    if payload.get("visible_to_consumer") is False:
        return False
    if publication_status_for(row, payload) not in VISIBLE_PUBLICATION_STATUSES:
        return False
    if availability_for(row.get("status")) == "unavailable":
        return False
    source_module = public_source_module(module_name, payload)
    source_resource_type = public_source_resource_type(
        row.get("resource_type") or "", payload
    )
    title = first_text(
        payload,
        ("public_title", "name", "title", "headline", "category"),
        fallback=source_module,
    )
    description = first_text(
        payload, ("public_description", "description", "summary"), fallback=title
    )
    offer_type = normalize_offer_type(payload.get("offer_type")) or infer_offer_type(
        source_module, source_resource_type, title, description
    )
    activity_id = str(
        payload.get("business_activity_id")
        or business_activity_for(
            source_module, source_resource_type, title, description
        )
    )
    allowed_types = BUSINESS_ACTIVITY_DEFINITIONS.get(activity_id, {}).get(
        "allowed_offer_types"
    )
    if allowed_types and offer_type not in allowed_types:
        return False
    if source_module in REGULATED_MODULES and default_compliance_status(
        source_module, payload
    ) not in {"approved", "verified"}:
        return False
    return True


def counted_facet(
    offers: list[dict[str, Any]],
    key: str,
    label_for: Any,
) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for offer in offers:
        value = str(offer.get(key) or "")
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return [
        {
            "id": value,
            "label": label_for(value),
            "count": count,
        }
        for value, count in sorted(
            counts.items(), key=lambda item: (str(label_for(item[0])), item[0])
        )
    ]


def consumer_action_for(
    module_name: str, resource_type: str, payload: dict[str, Any] | None = None
) -> str:
    if payload and payload.get("consumer_action"):
        return str(payload["consumer_action"])
    if module_name in {"marketplace", "stock"} and resource_type in {
        "products",
        "catalog_products",
        "discount_quotes",
    }:
        return "buy"
    if module_name in {"health", "services"}:
        return "book" if resource_type == "appointments" else "hire"
    if module_name == "jobs":
        return "apply"
    if module_name in {"delivery", "mobility", "property"}:
        return "request"
    return "view"


def action_label_for(action: str, business_activity_id: str | None) -> str:
    if action == "buy":
        return "Comprar"
    if action == "book":
        return "Marcar consulta" if business_activity_id == "saude" else "Agendar"
    if action == "hire":
        return (
            "Falar com advogado" if business_activity_id == "juridico" else "Contratar"
        )
    if action == "apply":
        return "Candidatar-se"
    if action == "request":
        return "Solicitar"
    if action == "coming_soon":
        return "Em breve"
    return "Ver detalhes"


def default_service_area(module_name: str, resource_type: str) -> str:
    if module_name in {"stock", "finance", "api_hub", "ai_core", "document", "bi"}:
        return "online"
    if resource_type in {"job_postings", "catalog_products", "discount_quotes"}:
        return "national"
    return "local"


def default_region_label(service_area: str) -> str:
    if service_area == "online":
        return "Online"
    if service_area == "national":
        return "Brasil"
    return "Regiao cadastrada"


def default_availability_type(module_name: str, resource_type: str) -> str:
    if module_name in {"marketplace", "stock", "wms", "erp"}:
        return "stock"
    if resource_type in {"appointments", "job_postings"}:
        return "agenda"
    if module_name in {"services", "delivery", "mobility", "riders", "property"}:
        return "region"
    return "sob_consulta"


def default_compliance_status(
    module_name: str, payload: dict[str, Any] | None = None
) -> str:
    if payload and payload.get("compliance_status"):
        return str(payload["compliance_status"]).casefold()
    return "pending_review" if module_name in REGULATED_MODULES else "not_required"


def business_activity_for(
    module_name: str, resource_type: str, title: str, description: str
) -> str:
    category = infer_category(module_name, resource_type, title, description)
    if category == "Comida e Mercado":
        return "alimentacao"
    if category == "Compras e Produtos":
        return "varejo"
    if category == "Saude e Bem-estar":
        return "saude"
    if category == "Casa, Reparos e Imoveis":
        return "imobiliario" if module_name == "property" else "servicos_domesticos"
    if category == "Mobilidade, Entregas e Logistica":
        return "logistica"
    if module_name == "jobs":
        return "empregos"
    if module_name in {"legal", "document"}:
        return "juridico"
    if module_name == "finance":
        return "financeiro"
    if category == "Tecnologia, Seguranca e IA":
        return "tecnologia"
    return "varejo" if module_name in {"marketplace", "stock"} else "tecnologia"


def business_activity_label(activity_id: str) -> str:
    definition = BUSINESS_ACTIVITY_DEFINITIONS.get(activity_id)
    if not definition:
        return "Ofertas profissionais"
    return str(definition["label_for_consumer"])


def company_category_for(module_name: str, business_activity_id: str | None) -> str:
    if business_activity_id and business_activity_id in BUSINESS_ACTIVITY_DEFINITIONS:
        return str(
            BUSINESS_ACTIVITY_DEFINITIONS[business_activity_id]["parent_category"]
        )
    if module_name in {"marketplace", "stock", "wms", "erp"}:
        return "Comercio"
    if module_name in {"services", "delivery", "mobility", "riders"}:
        return "Servicos"
    if module_name == "health":
        return "Saude"
    if module_name in {"legal", "document"}:
        return "Juridico"
    return "Tecnologia"


def company_type_label(company_type: Any) -> str:
    key = str(company_type or "microempresa").casefold()
    return COMPANY_TYPE_ALIASES.get(key, "Empresa participante")


def short_description(description: str, fallback: str) -> str:
    text = " ".join(str(description or fallback).split())
    if len(text) <= 160:
        return text
    return text[:157].rstrip() + "..."


def slugify(value: str) -> str:
    return (
        value.casefold()
        .replace(" ", "_")
        .replace(",", "")
        .replace("-", "_")
        .replace("__", "_")
    )


def friendly_module_title(slug: str, title: str) -> str:
    overrides = {
        "identity": "Cadastro e acesso",
        "business": "Empresas participantes",
        "permissions": "Perfis e permissoes",
        "finance": "Wallet, Gold e Pepitas",
        "marketplace": "Lojas e produtos locais",
        "stock": "Produtos com beneficios",
        "delivery": "Comida, entregas e coletas",
        "riders": "Entregadores e motoristas",
        "services": "Servicos profissionais",
        "mobility": "Corridas e transporte",
        "jobs": "Vagas e oportunidades",
        "erp": "Gestao e contabilidade",
        "wms": "Estoque e armazem",
        "tms": "Fretes e logistica",
        "crm": "Atendimento e relacionamento",
        "bpm": "Processos e automacao",
        "document": "Documentos e assinaturas",
        "hr": "Pessoas, cursos e RH",
        "health": "Saude e bem-estar",
        "legal": "Advocacia e juridico",
        "property": "Imoveis e manutencao",
        "bi": "Indicadores e relatorios",
        "ai_core": "Inteligencia artificial",
        "api_hub": "Integracoes digitais",
    }
    return overrides.get(slug, title)


def deduplicate_offers(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result = []
    for offer in offers:
        if offer["offer_id"] in seen:
            continue
        seen.add(offer["offer_id"])
        result.append(offer)
    return result
