from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "module_catalog.json"
OUTPUT_PATH = ROOT / "config" / "events" / "domain_event_fixtures.json"
FIXTURE_VERSION = "2026-06-30"
EXCHANGE = "all-in-one.domain"


def build_fixtures(catalog: dict) -> dict:
    modules: dict[str, dict] = {}
    event_count = 0

    for module in catalog.get("modules", []):
        slug = module["slug"]
        title = module["title"]
        routing_keys = list(module.get("events", []))
        events = []

        for index, routing_key in enumerate(routing_keys, start=1):
            seed = f"all-in-one-fixture:{slug}:{routing_key}"
            event_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"event:{seed}"))
            correlation_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"correlation:{seed}"))
            aggregate_type = routing_key.rsplit(".", 1)[0]
            aggregate_id = f"{slug}-fixture-{index:02d}"
            events.append(
                {
                    "event_id": event_id,
                    "routing_key": routing_key,
                    "aggregate_type": aggregate_type,
                    "aggregate_id": aggregate_id,
                    "entity_id": aggregate_id,
                    "actor_user_id": f"{slug}-fixture-actor",
                    "correlation_id": correlation_id,
                    "schema_version": 1,
                    "occurred_at": "2026-06-30T00:00:00Z",
                    "payload": {
                        "module": slug,
                        "routing_key": routing_key,
                        "summary": f"Fixture de evento do modulo {title}",
                    },
                }
            )

        modules[slug] = {
            "title": title,
            "routing_keys": routing_keys,
            "events": events,
        }
        event_count += len(events)

    return {
        "version": FIXTURE_VERSION,
        "source_catalog": "config/module_catalog.json",
        "source_catalog_version": catalog.get("version"),
        "exchange": EXCHANGE,
        "module_count": len(modules),
        "event_count": event_count,
        "modules": modules,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o catalogo de fixtures de eventos de dominio.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Apenas compara o arquivo gerado com o artefato versionado.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Caminho de saida do JSON gerado.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    rendered = json.dumps(build_fixtures(catalog), ensure_ascii=False, indent=2) + "\n"

    if args.check:
        if not output_path.is_file():
            print(f"Arquivo ausente: {output_path.relative_to(ROOT)}")
            return 1
        current = output_path.read_text(encoding="utf-8")
        if current != rendered:
            print(f"Arquivo desatualizado: {output_path.relative_to(ROOT)}")
            return 1
        print(f"Catalogo de fixtures validado: {output_path.relative_to(ROOT)}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Generated {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
