"""Runtime e validacao da onda de inovacao aprovada para os 24 modulos ativos."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = ROOT / "config" / "innovation_wave_001.json"
MODULE_CATALOG_PATH = ROOT / "config" / "module_catalog.json"
EXPECTED_INITIATIVE_IDS = {
    *(f"INNOV-{number:03d}" for number in range(1, 23)),
    "INNOV-024",
    "INNOV-025",
}
TRUTHY = {"1", "true", "yes", "on", "enabled"}
FALSY = {"0", "false", "no", "off", "disabled"}


class InnovationCatalogError(ValueError):
    """Indica divergencia entre a onda de inovacao e a fonte oficial de modulos."""


@dataclass(frozen=True, slots=True)
class InnovationDefinition:
    id: str
    module: str
    title: str
    priority: str
    feature_flag: str
    depends_on: tuple[str, ...]

    @property
    def environment_variable(self) -> str:
        normalized = self.feature_flag.upper().replace(".", "_").replace("-", "_")
        return f"ALL_IN_ONE_{normalized}"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InnovationCatalogError(f"Arquivo obrigatorio ausente: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InnovationCatalogError(f"JSON invalido em {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InnovationCatalogError(f"Catalogo deve ser um objeto JSON: {path}")
    return payload


def _active_modules() -> set[str]:
    catalog = _read_json(MODULE_CATALOG_PATH)
    modules = catalog.get("modules")
    if not isinstance(modules, list):
        raise InnovationCatalogError("config/module_catalog.json nao possui modules validos")
    slugs = {
        str(item.get("slug", "")).strip()
        for item in modules
        if isinstance(item, dict) and str(item.get("slug", "")).strip()
    }
    declared_count = catalog.get("module_count")
    if declared_count != len(slugs):
        raise InnovationCatalogError(
            f"module_catalog declara {declared_count}, mas possui {len(slugs)} modulos unicos"
        )
    return slugs


def validate_innovation_catalog(payload: Mapping[str, Any]) -> tuple[InnovationDefinition, ...]:
    initiatives = payload.get("initiatives")
    if not isinstance(initiatives, list):
        raise InnovationCatalogError("initiatives deve ser uma lista")

    definitions: list[InnovationDefinition] = []
    for raw in initiatives:
        if not isinstance(raw, dict):
            raise InnovationCatalogError("Cada iniciativa deve ser um objeto")
        try:
            definition = InnovationDefinition(
                id=str(raw["id"]).strip(),
                module=str(raw["module"]).strip(),
                title=str(raw["title"]).strip(),
                priority=str(raw["priority"]).strip(),
                feature_flag=str(raw["feature_flag"]).strip(),
                depends_on=tuple(str(value).strip() for value in raw.get("depends_on", [])),
            )
        except KeyError as exc:
            raise InnovationCatalogError(f"Campo obrigatorio ausente: {exc.args[0]}") from exc
        if not all(
            [definition.id, definition.module, definition.title, definition.feature_flag]
        ):
            raise InnovationCatalogError(f"Iniciativa incompleta: {raw!r}")
        if definition.priority not in {"P0", "P1", "P2"}:
            raise InnovationCatalogError(
                f"Prioridade invalida em {definition.id}: {definition.priority}"
            )
        definitions.append(definition)

    active_modules = _active_modules()
    selected_modules = {item.module for item in definitions}
    initiative_ids = {item.id for item in definitions}
    flags = {item.feature_flag for item in definitions}
    forbidden = {str(value).strip() for value in payload.get("forbidden_modules", [])}

    if "vision" not in forbidden:
        raise InnovationCatalogError("Vision deve permanecer explicitamente proibido")
    if "vision" in selected_modules or "vision" in active_modules:
        raise InnovationCatalogError("Vision nao pode constar entre os modulos ativos")
    if len(definitions) != len(initiative_ids):
        raise InnovationCatalogError("Existem IDs de iniciativas duplicados")
    if len(definitions) != len(selected_modules):
        raise InnovationCatalogError("Cada modulo ativo deve possuir exatamente uma iniciativa")
    if len(definitions) != len(flags):
        raise InnovationCatalogError("Existem feature flags duplicadas")
    if initiative_ids != EXPECTED_INITIATIVE_IDS:
        missing = sorted(EXPECTED_INITIATIVE_IDS - initiative_ids)
        extra = sorted(initiative_ids - EXPECTED_INITIATIVE_IDS)
        raise InnovationCatalogError(f"Numeracao divergente; ausentes={missing}, extras={extra}")
    if selected_modules != active_modules:
        missing = sorted(active_modules - selected_modules)
        extra = sorted(selected_modules - active_modules)
        raise InnovationCatalogError(f"Cobertura divergente; ausentes={missing}, extras={extra}")
    if payload.get("module_count") != len(definitions):
        raise InnovationCatalogError("module_count diverge da quantidade de iniciativas")

    for definition in definitions:
        unknown_dependencies = set(definition.depends_on) - active_modules
        if unknown_dependencies:
            raise InnovationCatalogError(
                f"{definition.id} depende de modulos desconhecidos: {sorted(unknown_dependencies)}"
            )

    return tuple(sorted(definitions, key=lambda item: item.id))


@lru_cache(maxsize=4)
def load_innovation_catalog(
    path: str | Path = DEFAULT_CATALOG_PATH,
) -> tuple[InnovationDefinition, ...]:
    resolved = Path(path).resolve()
    return validate_innovation_catalog(_read_json(resolved))


def get_innovation(initiative_id: str) -> InnovationDefinition:
    normalized = initiative_id.strip().upper()
    for definition in load_innovation_catalog():
        if definition.id == normalized:
            return definition
    raise KeyError(f"Iniciativa nao encontrada: {initiative_id}")


def innovation_enabled(
    initiative_id: str,
    environment: Mapping[str, str] | None = None,
) -> bool:
    definition = get_innovation(initiative_id)
    values = os.environ if environment is None else environment
    raw_value = values.get(definition.environment_variable)
    if raw_value is None:
        return False
    normalized = raw_value.strip().casefold()
    if normalized in TRUTHY:
        return True
    if normalized in FALSY:
        return False
    raise InnovationCatalogError(
        f"Valor invalido para {definition.environment_variable}: {raw_value!r}"
    )


def innovation_summary() -> dict[str, Any]:
    definitions = load_innovation_catalog()
    return {
        "wave_id": "innovation-wave-001",
        "module_count": len(definitions),
        "priorities": {
            priority: sum(item.priority == priority for item in definitions)
            for priority in ("P0", "P1", "P2")
        },
        "enabled": [item.id for item in definitions if innovation_enabled(item.id)],
        "forbidden_modules": ["vision"],
    }
