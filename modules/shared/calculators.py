from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, Field


MONEY = Decimal("0.0001")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


class DeliveryQuoteRequest(BaseModel):
    distance_km: Decimal = Field(gt=0)
    duration_minutes: Decimal = Field(gt=0)
    weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    volume_m3: Decimal = Field(default=Decimal("0"), ge=0)
    vehicle_type: str = "motorcycle"
    toll_brl: Decimal = Field(default=Decimal("0"), ge=0)
    declared_value_brl: Decimal = Field(default=Decimal("0"), ge=0)
    insurance: bool = False
    urgent: bool = False
    helper: bool = False
    refrigerated: bool = False


def delivery_quote(body: DeliveryQuoteRequest) -> dict[str, str]:
    vehicle = {
        "bicycle": Decimal("4.00"),
        "motorcycle": Decimal("6.50"),
        "car": Decimal("10.00"),
        "van": Decimal("18.00"),
        "truck": Decimal("35.00"),
    }.get(body.vehicle_type, Decimal("10.00"))
    base = vehicle + body.distance_km * Decimal("1.75") + body.duration_minutes * Decimal("0.18")
    cargo = body.weight_kg * Decimal("0.04") + body.volume_m3 * Decimal("8.00")
    extras = body.toll_brl
    extras += Decimal("25.00") if body.helper else Decimal("0")
    extras += Decimal("18.00") if body.refrigerated else Decimal("0")
    subtotal = base + cargo + extras
    if body.urgent:
        subtotal *= Decimal("1.20")
    insurance_fee = body.declared_value_brl * Decimal("0.0125") if body.insurance else Decimal("0")
    total = money(subtotal + insurance_fee)
    platform_fee = money(total * Decimal("0.18"))
    return {
        "subtotal_brl": str(money(subtotal)),
        "insurance_brl": str(money(insurance_fee)),
        "platform_fee_brl": str(platform_fee),
        "total_brl": str(total),
    }


class MobilityFareRequest(BaseModel):
    distance_km: Decimal = Field(gt=0)
    duration_minutes: Decimal = Field(gt=0)
    vehicle_type: str = "economy"
    demand_multiplier: Decimal = Field(default=Decimal("1.00"), ge=Decimal("1.00"), le=Decimal("3.00"))


def mobility_fare(body: MobilityFareRequest) -> dict[str, str]:
    base, per_km, per_minute = {
        "economy": (Decimal("5.00"), Decimal("1.70"), Decimal("0.25")),
        "comfort": (Decimal("8.00"), Decimal("2.40"), Decimal("0.32")),
        "premium": (Decimal("14.00"), Decimal("3.80"), Decimal("0.45")),
    }.get(body.vehicle_type, (Decimal("5.00"), Decimal("1.70"), Decimal("0.25")))
    fare = money((base + body.distance_km * per_km + body.duration_minutes * per_minute) * body.demand_multiplier)
    return {"fare_brl": str(fare), "platform_fee_brl": str(money(fare * Decimal("0.20")))}


class CommissionRequest(BaseModel):
    gross_brl: Decimal = Field(gt=0)
    commission_percent: Decimal = Field(ge=Decimal("8"), le=Decimal("15"))


def marketplace_commission(body: CommissionRequest) -> dict[str, str]:
    commission = money(body.gross_brl * body.commission_percent / Decimal("100"))
    return {"commission_brl": str(commission), "seller_net_brl": str(money(body.gross_brl - commission))}
