from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP


ROUNDING_MODES = {
    "half_up": ROUND_HALF_UP,
    "half_even": ROUND_HALF_EVEN,
    "floor": ROUND_FLOOR,
    "ceiling": ROUND_CEILING,
}


def decimal_value(value: Decimal | int | str) -> Decimal:
    if isinstance(value, float):
        raise TypeError("Float binario proibido; informe Decimal, inteiro ou string decimal.")
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Valor decimal invalido.") from exc
    if not result.is_finite():
        raise ValueError("Valor decimal deve ser finito.")
    return result


def quantize(value: Decimal, precision: int, rounding_mode: str) -> Decimal:
    if not 0 <= precision <= 12:
        raise ValueError("Precisao deve estar entre 0 e 12.")
    try:
        rounding = ROUNDING_MODES[rounding_mode]
    except KeyError as exc:
        raise ValueError("Modo de arredondamento nao permitido.") from exc
    return value.quantize(Decimal(1).scaleb(-precision), rounding=rounding)


@dataclass(frozen=True)
class ConversionRule:
    multiplier: Decimal | int | str
    divisor: Decimal | int | str
    precision: int
    rounding_mode: str
    source_dimension: str
    target_dimension: str
    effective_from: datetime
    effective_to: datetime | None = None
    approved: bool = False
    density: Decimal | int | str | None = None


def convert_quantity(
    quantity: Decimal | int | str,
    rule: ConversionRule,
    *,
    at: datetime | None = None,
) -> Decimal:
    moment = at or datetime.now(UTC)
    if not rule.approved:
        raise ValueError("Conversao precisa estar aprovada.")
    if moment < rule.effective_from or (rule.effective_to is not None and moment >= rule.effective_to):
        raise ValueError("Conversao fora da vigencia.")
    multiplier = decimal_value(rule.multiplier)
    divisor = decimal_value(rule.divisor)
    if multiplier <= 0 or divisor <= 0:
        raise ValueError("Multiplicador e divisor devem ser positivos.")
    result = decimal_value(quantity) * multiplier / divisor
    if rule.source_dimension != rule.target_dimension:
        if rule.density is None:
            raise ValueError("Conversao entre dimensoes exige densidade contextual.")
        density = decimal_value(rule.density)
        if density <= 0:
            raise ValueError("Densidade deve ser positiva.")
        result *= density
    return quantize(result, rule.precision, rule.rounding_mode)


@dataclass(frozen=True)
class TaxRule:
    rate: Decimal | int | str
    base_reduction: Decimal | int | str
    precision: int
    rounding_mode: str
    legal_basis: str
    effective_from: datetime
    effective_to: datetime | None = None
    approved: bool = False


def calculate_tax(
    taxable_base: Decimal | int | str,
    rule: TaxRule,
    *,
    at: datetime | None = None,
) -> tuple[Decimal, Decimal]:
    moment = at or datetime.now(UTC)
    if not rule.approved:
        raise ValueError("Regra fiscal precisa estar aprovada.")
    if not rule.legal_basis.strip():
        raise ValueError("Fundamento legal obrigatorio.")
    if moment < rule.effective_from or (rule.effective_to is not None and moment >= rule.effective_to):
        raise ValueError("Regra fiscal fora da vigencia.")
    base = decimal_value(taxable_base)
    rate = decimal_value(rule.rate)
    reduction = decimal_value(rule.base_reduction)
    if base < 0 or rate < 0 or not Decimal("0") <= reduction <= Decimal("1"):
        raise ValueError("Base, aliquota ou reducao invalidas.")
    reduced_base = quantize(base * (Decimal("1") - reduction), rule.precision, rule.rounding_mode)
    amount = quantize(reduced_base * rate, rule.precision, rule.rounding_mode)
    return reduced_base, amount
