"""Repository para operações de delegações (Procuração Operacional Expirável).

Recurso 3: Procuração Operacional Expirável
Data: 26/07/2026
Branch: feature/primicias-selecionadas-v1
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC
from typing import Any
from uuid import uuid4

import psycopg
from psycopg import Connection, sql
from psycopg.rows import dict_row

from .correlation import get_correlation_id

UTC = UTC


class DelegationRepository:
    """Repository para gerenciar delegações com persistência PostgreSQL."""

    SCHEMA = "permissions"
    MAIN_TABLE = "delegations"
    CONSTRAINTS_TABLE = "delegation_constraints"
    USAGES_TABLE = "delegation_usages"
    REVOCATIONS_TABLE = "delegation_revocations"

    def __init__(self, dsn: str) -> None:
        """Inicializar repository com DSN do PostgreSQL."""
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        """Context manager para transações."""
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def create_delegation(
        self,
        grantor_id: str,
        grantee_id: str,
        purpose: str,
        constraints: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Criar nova delegação com constraints opcionais.

        Args:
            grantor_id: ID de quem concede a delegação
            grantee_id: ID de quem recebe a delegação
            purpose: Motivo/descrição da delegação
            constraints: Dict com max_amount, allowed_actions, etc
            idempotency_key: Chave para idempotência

        Returns:
            Dict com dados da delegação criada
        """
        delegation_id = str(uuid4())

        with self.transaction() as conn:
            # Insert delegação principal
            query = sql.SQL(
                """
                INSERT INTO {schema}.{table}
                (id, grantor_id, grantee_id, purpose, status, idempotency_key)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, grantor_id, grantee_id, purpose, status, created_at
                """
            ).format(
                schema=sql.Identifier(self.SCHEMA),
                table=sql.Identifier(self.MAIN_TABLE),
            )

            result = conn.execute(
                query,
                (
                    delegation_id,
                    grantor_id,
                    grantee_id,
                    purpose,
                    "pending",
                    idempotency_key,
                ),
            ).fetchone()

            # Insert constraints se fornecidas
            if constraints:
                constraint_id = str(uuid4())
                constraint_query = sql.SQL(
                    """
                    INSERT INTO {schema}.{table}
                    (id, delegation_id, valid_from, valid_until, max_amount,
                     allowed_actions, single_use)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                ).format(
                    schema=sql.Identifier(self.SCHEMA),
                    table=sql.Identifier(self.CONSTRAINTS_TABLE),
                )

                conn.execute(
                    constraint_query,
                    (
                        constraint_id,
                        delegation_id,
                        constraints.get("valid_from"),
                        constraints.get("valid_until"),
                        constraints.get("max_amount"),
                        constraints.get("allowed_actions", []),
                        constraints.get("single_use", False),
                    ),
                )

        # Preparar resposta
        return {
            "delegation_id": result["id"],
            "grantor_id": result["grantor_id"],
            "grantee_id": result["grantee_id"],
            "purpose": result["purpose"],
            "status": result["status"],
            "created_at": result["created_at"].isoformat()
            if result["created_at"]
            else None,
            "constraints": constraints or {},
        }

    def get_delegation(self, delegation_id: str) -> dict[str, Any] | None:
        """Recuperar delegação por ID.

        Args:
            delegation_id: UUID da delegação

        Returns:
            Dict com dados da delegação ou None se não existir
        """
        with self.transaction() as conn:
            # Get delegação principal
            query = sql.SQL(
                """
                SELECT id, grantor_id, grantee_id, purpose, status, created_at
                FROM {schema}.{table}
                WHERE id = %s
                """
            ).format(
                schema=sql.Identifier(self.SCHEMA),
                table=sql.Identifier(self.MAIN_TABLE),
            )

            result = conn.execute(query, (delegation_id,)).fetchone()

            if not result:
                return None

            # Get constraints
            constraint_query = sql.SQL(
                """
                SELECT valid_from, valid_until, max_amount, allowed_actions, single_use
                FROM {schema}.{table}
                WHERE delegation_id = %s
                LIMIT 1
                """
            ).format(
                schema=sql.Identifier(self.SCHEMA),
                table=sql.Identifier(self.CONSTRAINTS_TABLE),
            )

            constraints_row = conn.execute(
                constraint_query, (delegation_id,)
            ).fetchone()

            constraints = {}
            if constraints_row:
                constraints = {
                    "max_amount": constraints_row.get("max_amount"),
                    "allowed_actions": constraints_row.get("allowed_actions", []),
                    "single_use": constraints_row.get("single_use", False),
                    "valid_from": constraints_row.get("valid_from"),
                    "valid_until": constraints_row.get("valid_until"),
                }

        return {
            "delegation_id": result["id"],
            "grantor_id": result["grantor_id"],
            "grantee_id": result["grantee_id"],
            "purpose": result["purpose"],
            "status": result["status"],
            "created_at": result["created_at"].isoformat()
            if result["created_at"]
            else None,
            "constraints": constraints,
        }

    def update_delegation_status(
        self,
        delegation_id: str,
        new_status: str,
        updated_by: str | None = None,
    ) -> dict[str, Any] | None:
        """Atualizar status de delegação.

        Args:
            delegation_id: UUID da delegação
            new_status: Novo status (pending, active, revoked, completed)
            updated_by: ID de quem está atualizando

        Returns:
            Dict com dados atualizados ou None se não existir
        """
        with self.transaction() as conn:
            # Validar transição de status
            if new_status == "revoked" and updated_by:
                # Insert revocation record
                revocation_id = str(uuid4())
                revocation_query = sql.SQL(
                    """
                    INSERT INTO {schema}.{table}
                    (id, delegation_id, revoked_by)
                    VALUES (%s, %s, %s)
                    """
                ).format(
                    schema=sql.Identifier(self.SCHEMA),
                    table=sql.Identifier(self.REVOCATIONS_TABLE),
                )

                conn.execute(
                    revocation_query, (revocation_id, delegation_id, updated_by)
                )

            # Update main status
            update_query = sql.SQL(
                """
                UPDATE {schema}.{table}
                SET status = %s,
                    {status_field} = CASE
                        WHEN %s = 'active' THEN now()
                        WHEN %s = 'revoked' THEN now()
                        ELSE {status_field}
                    END
                WHERE id = %s
                RETURNING id, grantor_id, grantee_id, purpose, status, created_at
                """
            ).format(
                schema=sql.Identifier(self.SCHEMA),
                table=sql.Identifier(self.MAIN_TABLE),
                status_field=sql.Identifier(
                    "activated_at" if new_status == "active" else "revoked_at"
                ),
            )

            result = conn.execute(
                update_query,
                (new_status, new_status, new_status, delegation_id),
            ).fetchone()

            if not result:
                return None

            # Recuperar constraints
            constraint_query = sql.SQL(
                """
                SELECT max_amount, allowed_actions, single_use
                FROM {schema}.{table}
                WHERE delegation_id = %s
                LIMIT 1
                """
            ).format(
                schema=sql.Identifier(self.SCHEMA),
                table=sql.Identifier(self.CONSTRAINTS_TABLE),
            )

            constraints_row = conn.execute(
                constraint_query, (delegation_id,)
            ).fetchone()

            constraints = (
                {
                    "max_amount": constraints_row.get("max_amount"),
                    "allowed_actions": constraints_row.get("allowed_actions", []),
                    "single_use": constraints_row.get("single_use", False),
                }
                if constraints_row
                else {}
            )

        return {
            "delegation_id": result["id"],
            "grantor_id": result["grantor_id"],
            "grantee_id": result["grantee_id"],
            "purpose": result["purpose"],
            "status": result["status"],
            "created_at": result["created_at"].isoformat()
            if result["created_at"]
            else None,
            "constraints": constraints,
        }

    def record_usage(
        self,
        delegation_id: str,
        actor_id: str,
        module: str,
        action: str,
        amount: float | None = None,
        result: str = "allowed",
    ) -> dict[str, Any]:
        """Registrar uso de uma delegação.

        Args:
            delegation_id: UUID da delegação
            actor_id: ID de quem usou
            module: Módulo onde foi usada
            action: Ação executada
            amount: Quantia utilizada (se aplicável)
            result: Resultado (allowed, denied, limited)

        Returns:
            Dict com dados do registro de uso
        """
        usage_id = str(uuid4())
        correlation_id = get_correlation_id() or str(uuid4())

        with self.transaction() as conn:
            query = sql.SQL(
                """
                INSERT INTO {schema}.{table}
                (id, delegation_id, actor_id, module, action, amount,
                 correlation_id, result)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, delegation_id, actor_id, module, action,
                          amount, used_at, result
                """
            ).format(
                schema=sql.Identifier(self.SCHEMA),
                table=sql.Identifier(self.USAGES_TABLE),
            )

            result_row = conn.execute(
                query,
                (
                    usage_id,
                    delegation_id,
                    actor_id,
                    module,
                    action,
                    amount,
                    correlation_id,
                    result,
                ),
            ).fetchone()

        return {
            "usage_id": result_row["id"],
            "delegation_id": result_row["delegation_id"],
            "actor_id": result_row["actor_id"],
            "module": result_row["module"],
            "action": result_row["action"],
            "amount": result_row["amount"],
            "used_at": result_row["used_at"].isoformat()
            if result_row["used_at"]
            else None,
            "result": result_row["result"],
        }

    def close(self) -> None:
        """Fechar conexão com banco de dados."""
        if self.connection:
            self.connection.close()
