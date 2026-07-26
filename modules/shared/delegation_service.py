"""Service para operações de delegações com lógica de negócio.

Recurso 3: Procuração Operacional Expirável
Data: 26/07/2026
Branch: feature/primicias-selecionadas-v1
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException

from .delegation_repository import DelegationRepository

UTC = UTC


class DelegationService:
    """Service para delegações com lógica de negócio e validações."""

    def __init__(self):
        """Inicializar service com repository."""
        dsn = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/all_in_one",
        )
        self.repository = DelegationRepository(dsn)

    def create_delegation(
        self,
        grantor_id: str,
        grantee_id: str,
        purpose: str,
        constraints: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Criar delegação com validações de negócio.

        Validações:
        - max_amount não pode ser negativo
        - valid_until deve ser após valid_from
        - grantee_id e purpose são obrigatórios

        Args:
            grantor_id: ID de quem concede
            grantee_id: ID de quem recebe
            purpose: Descrição/motivo
            constraints: Restrições (max_amount, allowed_actions, etc)
            idempotency_key: Chave para idempotência

        Returns:
            Dict com delegação criada

        Raises:
            HTTPException: Se validações falharem
        """
        # Validações básicas
        if not grantee_id or not grantee_id.strip():
            raise HTTPException(status_code=422, detail="grantee_id é obrigatório")

        if not purpose or not purpose.strip():
            raise HTTPException(status_code=422, detail="purpose é obrigatório")

        # Validações de constraints
        if constraints:
            # Validar max_amount
            if constraints.get("max_amount") is not None:
                max_amount = constraints.get("max_amount")
                try:
                    max_amount = float(max_amount)
                    if max_amount < 0:
                        raise HTTPException(
                            status_code=422,
                            detail="max_amount deve ser positivo ou zero",
                        )
                except (TypeError, ValueError):
                    raise HTTPException(
                        status_code=422,
                        detail="max_amount deve ser um número",
                    )

            # Validar período válido
            if (
                constraints.get("valid_from") is not None
                and constraints.get("valid_until") is not None
            ):
                try:
                    valid_from = datetime.fromisoformat(
                        str(constraints.get("valid_from")).replace("Z", "+00:00")
                    )
                    valid_until = datetime.fromisoformat(
                        str(constraints.get("valid_until")).replace("Z", "+00:00")
                    )

                    if valid_until <= valid_from:
                        raise HTTPException(
                            status_code=422,
                            detail="valid_until deve ser após valid_from",
                        )
                except ValueError as e:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Formato de data inválido: {str(e)}",
                    )

        try:
            return self.repository.create_delegation(
                grantor_id=grantor_id,
                grantee_id=grantee_id,
                purpose=purpose,
                constraints=constraints,
                idempotency_key=idempotency_key,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar delegação: {str(e)}",
            )

    def get_delegation(self, delegation_id: str) -> dict[str, Any]:
        """Recuperar delegação por ID.

        Args:
            delegation_id: UUID da delegação

        Returns:
            Dict com dados da delegação

        Raises:
            HTTPException: Se não encontrar
        """
        try:
            result = self.repository.get_delegation(delegation_id)
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Delegação {delegation_id} não encontrada",
                )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao recuperar delegação: {str(e)}",
            )

    def update_delegation(
        self,
        delegation_id: str,
        status: str | None = None,
        updated_by: str | None = None,
    ) -> dict[str, Any]:
        """Atualizar delegação.

        Args:
            delegation_id: UUID da delegação
            status: Novo status (pending, active, revoked, completed)
            updated_by: ID de quem está atualizando

        Returns:
            Dict com delegação atualizada

        Raises:
            HTTPException: Se não encontrar ou status inválido
        """
        # Validar status
        valid_statuses = {"pending", "active", "revoked", "completed"}
        if status and status not in valid_statuses:
            raise HTTPException(
                status_code=422,
                detail=f"Status inválido. Válidos: {', '.join(valid_statuses)}",
            )

        try:
            result = self.repository.update_delegation_status(
                delegation_id=delegation_id,
                new_status=status or "pending",
                updated_by=updated_by,
            )
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Delegação {delegation_id} não encontrada",
                )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar delegação: {str(e)}",
            )

    def record_usage(
        self,
        delegation_id: str,
        actor_id: str,
        module: str,
        action: str,
        amount: float | None = None,
    ) -> dict[str, Any]:
        """Registrar uso de delegação.

        Args:
            delegation_id: UUID da delegação
            actor_id: ID de quem usou
            module: Módulo
            action: Ação
            amount: Quantia (opcional)

        Returns:
            Dict com registro de uso
        """
        try:
            return self.repository.record_usage(
                delegation_id=delegation_id,
                actor_id=actor_id,
                module=module,
                action=action,
                amount=amount,
                result="allowed",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao registrar uso: {str(e)}",
            )

    def __del__(self):
        """Limpar recurso ao destruir service."""
        try:
            self.repository.close()
        except Exception:
            pass
