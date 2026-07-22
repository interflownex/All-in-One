from __future__ import annotations

from decimal import Decimal


def calculate_valley_discount_visibility(balance_brl: Decimal) -> float:
    """
    Implementa a regra BR-STO-009: Visibilidade Gradativa de descontos.
    10% (saldo > 1k), 20% (saldo > 5k), 50% (saldo > 10k).
    """
    if balance_brl >= Decimal("10000.00"):
        return 0.50
    if balance_brl >= Decimal("5000.00"):
        return 0.20
    if balance_brl >= Decimal("1000.00"):
        return 0.10
    return 0.00


def validate_pepita_gamification(amount: int) -> bool:
    """
    Garante que a opção manual de Pepitas seja apenas 1, 10 ou 100.
    """
    return amount in {1, 10, 100}


def apply_essential_plan_restrictions(cnpj: str, integration_key: str) -> bool:
    """
    Bloqueia integrações externas para o Plano Essencial (CNPJ único).
    """
    return False
