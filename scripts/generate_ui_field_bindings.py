#!/usr/bin/env python3
"""Gera contratos UI tipados a partir de migrations e regras de domínio versionadas."""

from __future__ import annotations

import json
import re
from pathlib import Path

from generate_data_audit_inventory import ROOT, discover_logical_rules, discover_physical_model


OUTPUT = ROOT / "apps" / "all-in-one" / "src" / "config" / "entityFieldBindings.generated.json"
SYSTEM_FIELDS = {
    "id", "user_id", "created_at", "updated_at", "deleted_at", "created_by", "updated_by",
    "idempotency_key", "metadata", "status", "schema_version", "row_hash", "previous_hash",
}
WORD_LABELS = {
    "name": "Nome", "full": "completo", "legal": "empresarial", "description": "Descrição",
    "title": "Título", "type": "Tipo", "number": "Número", "email": "E-mail", "phone": "Telefone",
    "document": "Documento", "date": "Data", "time": "hora", "start": "início", "end": "fim",
    "amount": "Valor", "price": "Preço", "cost": "Custo", "currency": "Moeda", "quantity": "Quantidade",
    "address": "Endereço", "city": "Cidade", "state": "Estado", "country": "País", "postal": "CEP",
    "reason": "Motivo", "notes": "Observações", "code": "Código", "category": "Categoria",
    "url": "URL", "key": "Chave", "value": "Valor", "enabled": "Habilitado", "active": "Ativo",
    "company": "Empresa", "store": "Loja", "product": "Produto", "order": "Pedido", "user": "Usuário",
    "owner": "Responsável", "provider": "Prestador", "employee": "Funcionário", "patient": "Paciente",
}


def label_for(name: str) -> str:
    words = [WORD_LABELS.get(word, word) for word in name.split("_")]
    return " ".join(words).capitalize()


def component_for(name: str, physical_type: str) -> tuple[str, str]:
    lowered = physical_type.casefold()
    if "bool" in lowered:
        return "checkbox", "boolean"
    if name.endswith("_at") or "timestamp" in lowered:
        return "datetime-local", "datetime"
    if name.endswith("_on") or re.search(r"\bdate\b", lowered):
        return "date", "date"
    if any(token in lowered for token in ("numeric", "decimal", "integer", "bigint", "smallint", "real")):
        return "number", "number"
    if any(token in lowered for token in ("json", "array")) or lowered.endswith("[]"):
        return "textarea", "json"
    if "email" in name:
        return "email", "string"
    if any(token in name for token in ("description", "summary", "notes", "content", "payload", "details")):
        return "textarea", "string"
    if "url" in name:
        return "url", "string"
    return "text", "string"


def max_length(physical_type: str) -> int | None:
    match = re.search(r"(?:VARCHAR|CHARACTER VARYING)\s*\((\d+)\)", physical_type, re.I)
    return int(match.group(1)) if match else None


def main() -> None:
    _, tables, _, _ = discover_physical_model()
    logical = discover_logical_rules(tables, [])
    contracts: dict[str, object] = {}
    for entity in logical:
        module = str(entity["module"])
        resource = str(entity["entity"])
        target = str(entity["physical_storage_target"])
        required_by_rule = set(entity["required_fields"])
        fields = []
        for field in tables.get(target, []):
            if field.physical_name in SYSTEM_FIELDS:
                continue
            component, logical_type = component_for(field.physical_name, field.physical_type)
            required = field.physical_name in required_by_rule or (
                not field.nullable and not field.default and not field.primary_key
            )
            fields.append({
                "name": field.physical_name,
                "label": label_for(field.physical_name),
                "component": component,
                "logicalType": logical_type,
                "required": required,
                "readOnly": bool(entity["immutable"]),
                "sensitive": field.lgpd != "não classificado automaticamente",
                "maxLength": max_length(field.physical_type),
                "physicalType": field.physical_type,
                "binding": f"ResourceCreate.payload.{field.physical_name}",
                "patchBinding": f"ResourcePatch.payload.{field.physical_name}",
                "storage": f"{target}.{field.physical_name}",
                "validation": "required + backend domain rule" if required else "backend domain rule",
                "evidence": field.evidence,
            })
        if not fields:
            raise RuntimeError(f"Entidade sem campo de interface elegível: {module}.{resource} ({target})")
        contracts[f"{module}:{resource}"] = {
            "module": module, "resource": resource, "endpoint": f"/{module}/resources/{resource}",
            "createDto": "ResourceCreate", "patchDto": "ResourcePatch", "physicalStorage": target,
            "immutable": bool(entity["immutable"]), "sensitive": bool(entity["sensitive"]),
            "fields": fields, "listFields": [item["name"] for item in fields[:6]],
            "bindingStatus": "verified_physical_dto_contract",
            "ruleEvidence": entity["evidence"],
        }
    payload = {"version": 1, "generatedFrom": ["database/postgres/migrations", "modules/shared/domain_rules.py"],
               "contractCount": len(contracts), "contracts": contracts}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)), "contracts": len(contracts),
                      "fields": sum(len(item["fields"]) for item in contracts.values())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
