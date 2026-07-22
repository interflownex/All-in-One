from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

import psycopg
from psycopg import Connection, sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .audit_contract import insert_postgres_audit
from .correlation import get_correlation_id
from .event_contract import EVENT_SCHEMA_VERSION, build_event_envelope
from .generic_postgres_resource import insert_generic_resource, update_generic_resource
from .store import DuplicateValueError

TABLES = {
    "wallets": "finance.wallets",
    "ledger_entries": "finance.ledger_entries",
    "escrows": "finance.escrows",
    "valley_gold_ledger_entries": "finance.valley_gold_ledger_entries",
    "splits": "finance.splits",
    "invoices": "finance.invoices",
}


class FinancePostgresStore:
    """Production Finance adapter backed by typed PostgreSQL relations (wallets, ledger, escrow)."""

    module = "finance"
    backend = "postgres_finance_typed_store"

    def __init__(self, dsn: str) -> None:
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)

    @staticmethod
    def _table(resource_type: str) -> sql.Identifier:
        schema_name, table_name = TABLES[resource_type].split(".", maxsplit=1)
        return sql.Identifier(schema_name, table_name)

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    @staticmethod
    def _payload(row: dict[str, Any]) -> dict[str, Any]:
        return dict((row.get("metadata") or {}).get("runtime_payload", {}))

    def _resource(
        self, resource_type: str, row: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        if row is None:
            return None
        created_at = row.get("created_at")
        if created_at is None:
            raise RuntimeError(
                f"PostgreSQL nao retornou timestamp para {resource_type}."
            )
        return {
            "id": str(row["id"]),
            "module": self.module,
            "resource_type": resource_type,
            "user_id": str(row["user_id"]),
            "status": row["status"],
            "payload": self._resource_payload(resource_type, row),
            "created_at": created_at.isoformat(),
            "updated_at": (row.get("updated_at") or created_at).isoformat(),
        }

    def _resource_payload(
        self, resource_type: str, row: dict[str, Any]
    ) -> dict[str, Any]:
        payload = self._payload(row)
        if resource_type == "wallets":
            return {
                **payload,
                "brl_available": str(row.get("brl_available", 0)),
                "nex_available": str(row.get("nex_available", 0)),
            }
        if resource_type == "valley_gold_ledger_entries":
            return {
                **payload,
                "merchant_business_id": str(row["merchant_business_id"]),
                "entry_type": row["entry_type"],
                "amount_gold_delta": row["amount_gold_delta"],
                "reference_type": row["reference_type"],
                "reference_id": str(row["reference_id"])
                if row.get("reference_id")
                else None,
            }
        return payload

    def create(
        self,
        resource_type: str,
        user_id: str,
        entity_id: str | None,
        status: str,
        payload: dict[str, Any],
        actor: str,
        unique_fields: tuple[str, ...],
        event: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        resource_id = str(uuid4())
        try:
            with self.transaction() as connection:
                row = self._insert(
                    connection,
                    resource_type,
                    resource_id,
                    user_id,
                    entity_id,
                    status,
                    payload,
                    actor,
                    idempotency_key,
                )
                item = self._resource(resource_type, row)
                if item is None:
                    raise RuntimeError(
                        f"Erro ao criar recurso Finance {resource_type}."
                    )

                insert_postgres_audit(
                    connection,
                    module=self.module,
                    actor_user_id=actor,
                    action="create",
                    resource_type=resource_type,
                    resource_id=resource_id,
                    before=None,
                    after=item,
                    user_id=user_id,
                    company_id=entity_id,
                )

                self._event(connection, event, actor, item)
                return item
        except Exception as exc:
            if "unique" in str(exc).lower():
                raise DuplicateValueError(resource_type) from exc
            raise

    def _insert(
        self,
        connection,
        resource_type,
        resource_id,
        user_id,
        entity_id,
        status,
        payload,
        actor,
        idempotency_key,
    ):
        metadata = Jsonb({"runtime_payload": payload})
        if resource_type == "wallets":
            return connection.execute(
                """INSERT INTO finance.wallets (id, user_id, wallet_type, status, metadata, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload.get("wallet_type", "personal"),
                    status,
                    metadata,
                    actor,
                ),
            ).fetchone()

        if resource_type == "ledger_entries":
            return connection.execute(
                """INSERT INTO finance.ledger_entries 
                   (id, user_id, wallet_id, currency, amount_brl, amount_nex, entry_type, idempotency_key, metadata, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["wallet_id"],
                    payload["currency"],
                    payload.get("amount_brl"),
                    payload.get("amount_nex"),
                    payload["entry_type"],
                    idempotency_key or str(uuid4()),
                    metadata,
                    actor,
                ),
            ).fetchone()

        if resource_type == "valley_gold_ledger_entries":
            return connection.execute(
                """INSERT INTO finance.valley_gold_ledger_entries
                   (id, user_id, merchant_business_id, entry_type, amount_gold_delta,
                    reference_type, reference_id, status, metadata, created_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["merchant_business_id"],
                    payload["entry_type"],
                    payload["amount_gold_delta"],
                    payload["reference_type"],
                    payload.get("reference_id"),
                    status,
                    metadata,
                    actor,
                    idempotency_key or str(uuid4()),
                ),
            ).fetchone()

        return insert_generic_resource(
            connection,
            TABLES[resource_type],
            resource_id,
            user_id,
            entity_id,
            status,
            payload,
            actor,
            idempotency_key,
        )

    def update(
        self,
        item: dict[str, Any],
        payload: dict[str, Any],
        status: str,
        actor: str,
        action: str,
        event: str | None = None,
    ) -> dict[str, Any]:
        before = {**item, "payload": dict(item["payload"])}
        with self.transaction() as connection:
            row = update_generic_resource(
                connection,
                TABLES[item["resource_type"]],
                item["id"],
                payload,
                status,
                actor,
            )
            updated = self._resource(item["resource_type"], row)
            if updated is None:
                raise RuntimeError(
                    "PostgreSQL nao retornou recurso Finance atualizado."
                )
            insert_postgres_audit(
                connection,
                module="finance",
                actor_user_id=actor,
                action=action,
                resource_type=item["resource_type"],
                resource_id=item["id"],
                before=before,
                after=updated,
                user_id=item["user_id"],
                company_id=item["entity_id"],
            )
            if event:
                self._event(connection, event, actor, updated)
            return updated

    def soft_delete(self, item: dict[str, Any], actor: str) -> None:
        with self.transaction() as connection:
            connection.execute(
                sql.SQL(
                    "UPDATE {} SET deleted_at = NOW(), updated_by = %s, updated_at = NOW() WHERE id = %s"
                ).format(self._table(item["resource_type"])),
                (actor, item["id"]),
            )
            insert_postgres_audit(
                connection,
                module="finance",
                actor_user_id=actor,
                action="soft_delete",
                resource_type=item["resource_type"],
                resource_id=item["id"],
                before=item,
                after=None,
                user_id=item["user_id"],
                company_id=item["entity_id"],
            )

    def list(
        self, resource_type: str, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        query = sql.SQL("SELECT * FROM {}").format(self._table(resource_type))
        params = []
        if user_id:
            query += sql.SQL(" WHERE user_id = %s")
            params.append(user_id)

        rows = self.connection.execute(query, params).fetchall()
        return [self._resource(resource_type, row) for row in rows]

    def get(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE id = %s").format(
                self._table(resource_type)
            ),
            (resource_id,),
        ).fetchone()
        return self._resource(resource_type, row)

    def execute_transfer(
        self,
        actor_user_id: str,
        source_wallet_id: str,
        dest_wallet_id: str,
        amount: Decimal,
        currency: str,
        description: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM finance.ledger_entries WHERE idempotency_key = %s",
                (idempotency_key,),
            ).fetchone()
            if existing:
                return {"status": "already_processed", "entry_id": str(existing["id"])}

            col_avail = "brl_available" if currency == "BRL" else "nex_available"
            source = connection.execute(
                sql.SQL(
                    "SELECT * FROM finance.wallets WHERE id = %s FOR UPDATE"
                ).format(),
                (source_wallet_id,),
            ).fetchone()

            if not source or source[col_avail] < amount:
                raise ValueError("Saldo insuficiente ou carteira nao encontrada.")

            connection.execute(
                sql.SQL(
                    "UPDATE finance.wallets SET {} = {} - %s, updated_at = NOW() WHERE id = %s"
                ).format(sql.Identifier(col_avail), sql.Identifier(col_avail)),
                (amount, source_wallet_id),
            )
            connection.execute(
                sql.SQL(
                    "UPDATE finance.wallets SET {} = {} + %s, updated_at = NOW() WHERE id = %s"
                ).format(sql.Identifier(col_avail), sql.Identifier(col_avail)),
                (amount, dest_wallet_id),
            )

            entry_id = str(uuid4())
            connection.execute(
                """INSERT INTO finance.ledger_entries 
                   (id, user_id, wallet_id, counterparty_user_id, currency, amount_brl, amount_nex, 
                    entry_type, idempotency_key, metadata, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    entry_id,
                    source["user_id"],
                    source_wallet_id,
                    None,
                    currency,
                    amount if currency == "BRL" else None,
                    amount if currency == "NEX" else None,
                    "transfer_out",
                    idempotency_key,
                    Jsonb({"description": description}),
                    actor_user_id,
                ),
            )

            return {"status": "success", "entry_id": entry_id}

    def create_escrow(
        self,
        actor_user_id: str,
        user_id: str,
        wallet_id: str,
        beneficiary_user_id: str,
        amount: Decimal,
        release_condition: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            wallet = connection.execute(
                "SELECT * FROM finance.wallets WHERE id = %s AND user_id = %s FOR UPDATE",
                (wallet_id, user_id),
            ).fetchone()

            if not wallet or wallet["brl_available"] < amount:
                raise ValueError("Saldo insuficiente para criar garantia (Escrow).")

            connection.execute(
                """UPDATE finance.wallets 
                   SET brl_available = brl_available - %s, brl_held = brl_held + %s, updated_at = NOW() 
                   WHERE id = %s""",
                (amount, amount, wallet_id),
            )

            escrow_id = str(uuid4())
            connection.execute(
                """INSERT INTO finance.escrows 
                   (id, user_id, wallet_id, beneficiary_user_id, amount_brl, release_condition, status, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    escrow_id,
                    user_id,
                    wallet_id,
                    beneficiary_user_id,
                    amount,
                    Jsonb(release_condition),
                    "held",
                    actor_user_id,
                ),
            )

            connection.execute(
                """INSERT INTO finance.ledger_entries 
                   (id, user_id, wallet_id, currency, amount_brl, entry_type, idempotency_key, metadata, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(uuid4()),
                    user_id,
                    wallet_id,
                    "BRL",
                    amount,
                    "escrow_hold",
                    idempotency_key,
                    Jsonb({"escrow_id": escrow_id}),
                    actor_user_id,
                ),
            )

            return {"id": escrow_id, "status": "held", "amount": str(amount)}

    def release_escrow(self, actor_user_id: str, escrow_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            escrow = connection.execute(
                "SELECT * FROM finance.escrows WHERE id = %s FOR UPDATE", (escrow_id,)
            ).fetchone()

            if not escrow or escrow["status"] != "held":
                raise ValueError(
                    "Escrow nao encontrado ou nao esta em estado de retenção."
                )

            connection.execute(
                "UPDATE finance.wallets SET brl_held = brl_held - %s, updated_at = NOW() WHERE id = %s",
                (escrow["amount_brl"], escrow["wallet_id"]),
            )

            beneficiary_wallet = connection.execute(
                "SELECT id FROM finance.wallets WHERE user_id = %s AND wallet_type = 'personal' LIMIT 1",
                (escrow["beneficiary_user_id"],),
            ).fetchone()

            if not beneficiary_wallet:
                raise ValueError("Carteira do beneficiario nao encontrada.")

            connection.execute(
                "UPDATE finance.wallets SET brl_available = brl_available + %s, updated_at = NOW() WHERE id = %s",
                (escrow["amount_brl"], beneficiary_wallet["id"]),
            )

            connection.execute(
                "UPDATE finance.escrows SET status = 'released', updated_at = NOW(), updated_by = %s WHERE id = %s",
                (actor_user_id, escrow_id),
            )

            connection.execute(
                """INSERT INTO finance.ledger_entries 
                   (id, user_id, wallet_id, currency, amount_brl, entry_type, idempotency_key, metadata, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    str(uuid4()),
                    escrow["beneficiary_user_id"],
                    beneficiary_wallet["id"],
                    "BRL",
                    escrow["amount_brl"],
                    "escrow_settlement",
                    str(uuid4()),
                    Jsonb({"escrow_id": escrow_id}),
                    actor_user_id,
                ),
            )

            return {"id": escrow_id, "status": "released"}

    def metrics(self) -> tuple[int, int, int]:
        count = self.connection.execute(
            "SELECT COUNT(*) FROM finance.wallets"
        ).fetchone()["count"]
        audits = self.connection.execute(
            "SELECT COUNT(*) FROM audit.logs WHERE module = 'finance'"
        ).fetchone()["count"]
        events = self.connection.execute(
            "SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE 'payment.%' OR routing_key LIKE 'finance.%'"
        ).fetchone()["count"]
        return count, audits, events

    def _event(
        self, connection: Connection, routing_key: str, actor: str, item: dict[str, Any]
    ) -> None:
        correlation_id = get_correlation_id()
        envelope = build_event_envelope(
            module=self.module,
            routing_key=routing_key,
            actor_user_id=actor,
            item=item,
            correlation_id=correlation_id,
        )
        connection.execute(
            """INSERT INTO audit.domain_events
               (id, user_id, actor_user_id, entity_id, routing_key, aggregate_type, aggregate_id,
                correlation_id, schema_version, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                envelope["event_id"],
                item["user_id"],
                actor,
                item.get("entity_id"),
                routing_key,
                item["resource_type"],
                item["id"],
                correlation_id,
                EVENT_SCHEMA_VERSION,
                Jsonb(envelope),
                actor,
            ),
        )
