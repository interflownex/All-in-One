import json


def generate_store(module):
    slug = module["slug"]
    entities = module["entities"]

    # Se ja existe um store customizado, nao sobrescrever
    if slug in [
        "identity",
        "finance",
        "jobs",
        "api_hub",
        "business",
        "marketplace",
        "delivery",
        "services",
        "mobility",
        "erp",
    ]:
        return

    content = f'''from __future__ import annotations

from typing import Any
from psycopg import Connection
from psycopg.types.json import Jsonb
from .postgres_store import BasePostgresStore

class {slug.title().replace("_", "")}PostgresStore(BasePostgresStore):
    """Production {slug.title()} adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "{slug}"
    backend = "postgres_{slug}_typed_store"
    tables = {{
'''
    for entity in entities:
        content += f'        "{entity}": "{slug}.{entity}",\n'

    content += f"""    }}
    soft_deletable = frozenset({entities})

    def _insert(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        user_id: str,
        entity_id: str | None,
        status: str,
        payload: dict[str, Any],
        actor: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        return self._insert_generic(
            connection, resource_type, resource_id, user_id, entity_id, status, payload, actor, idempotency_key
        )

    def _update(
        self, connection: Connection, resource_type: str, resource_id: str, payload: dict[str, Any], status: str, actor: str
    ) -> dict[str, Any]:
        return self._update_generic(connection, resource_type, resource_id, payload, status, actor)
"""

    file_path = f"modules/shared/{slug}_postgres_store.py"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {file_path}")


def main():
    with open("config/module_catalog.json", encoding="utf-8") as f:
        catalog = json.load(f)

    for module in catalog["modules"]:
        generate_store(module)


if __name__ == "__main__":
    main()
