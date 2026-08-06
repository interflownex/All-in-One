#!/usr/bin/env python3
"""Atualiza o painel público com percentuais do plano privado oficial."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MATRIX_START = "## 3. Matriz por modulo"
MATRIX_END = "## 4. Criterios de beta"
README_START = "<!-- PROJECT_PROGRESS_START -->"
README_END = "<!-- PROJECT_PROGRESS_END -->"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, default=Path("."))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/module-progress-stages.json"),
    )
    return parser.parse_args()


def read(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {path}")
    return path.read_text(encoding="utf-8")


def matrix_from_plan(text: str) -> dict[str, int]:
    if MATRIX_START not in text or MATRIX_END not in text:
        raise ValueError("Matriz por módulo não localizada no plano de execução.")
    section = text.split(MATRIX_START, 1)[1].split(MATRIX_END, 1)[0]
    rows = re.findall(
        r"^\|\s*`([^`]+)`\s*\|\s*(\d+)%\s*\|",
        section,
        flags=re.MULTILINE,
    )
    if not rows:
        raise ValueError("Nenhum percentual foi extraído do plano oficial.")
    return {slug.strip(): int(percent) for slug, percent in rows}


def catalog_from_file(path: Path) -> dict[str, dict[str, str]]:
    payload = json.loads(read(path))
    return {
        item["slug"]: {
            "title": item.get("title", item["slug"]),
            "description": item.get("description", ""),
        }
        for item in payload.get("modules", [])
    }


def state(percent: int) -> str:
    if percent >= 90:
        return "Beta técnico"
    if percent >= 80:
        return "Consolidação"
    if percent >= 70:
        return "Integração"
    if percent >= 60:
        return "Desenvolvimento"
    return "Fundação"


def configured_values(matrix: dict[str, int], config: dict) -> list[int]:
    slugs = [slug for stage in config["stages"] for slug in stage["modules"]]
    missing = [slug for slug in slugs if slug not in matrix]
    extra = sorted(set(matrix) - set(slugs))
    if missing:
        raise ValueError("Percentuais ausentes: " + ", ".join(missing))
    if extra:
        raise ValueError("Módulos sem etapa pública: " + ", ".join(extra))
    return [matrix[slug] for slug in slugs]


def render_modules(
    matrix: dict[str, int],
    catalog: dict[str, dict[str, str]],
    config: dict,
    now: datetime,
) -> str:
    values = configured_values(matrix, config)
    stage_rows: list[str] = []
    module_rows: list[str] = []
    fallback_titles = config.get("fallback_titles", {})
    fallback_descriptions = config.get("fallback_descriptions", {})

    for stage in config["stages"]:
        stage_values = [matrix[slug] for slug in stage["modules"]]
        stage_rows.append(
            f"| Etapa {stage['id']} | {stage['title']} | "
            f"{round(sum(stage_values) / len(stage_values))}% | "
            + ", ".join(f"`{slug}`" for slug in stage["modules"])
            + " |"
        )
        for slug in stage["modules"]:
            info = catalog.get(slug, {})
            title = info.get("title") or fallback_titles.get(slug) or slug
            description = (
                info.get("description")
                or fallback_descriptions.get(slug)
                or "Escopo público em consolidação."
            )
            module_rows.append(
                f"| {stage['id']} | **{title}** | {description} | "
                f"**{matrix[slug]}%** | {state(matrix[slug])} |"
            )

    explanations = "\n\n".join(
        f"### Etapa {stage['id']}: {stage['title']}\n\n{stage['objective']}"
        for stage in config["stages"]
    )
    overall = round(sum(values) / len(values))

    return f"""# Módulos e evolução do projeto

Este painel público apresenta os módulos previstos para o All-in-One + Valley, a ordem de implantação e o percentual consolidado de cada módulo.

> Os percentuais são extraídos do plano oficial de execução mantido no repositório privado. O painel público mostra somente evolução consolidada, sem tarefas, responsáveis, credenciais ou detalhes internos.

**Evolução total do projeto:** **{overall}%**

**Módulos acompanhados:** **{len(values)}**

**Última atualização:** {now.strftime('%d/%m/%Y às %H:%M')} (America/Sao_Paulo)

**Frequência:** atualização automática diária.

<!-- MODULE_PROGRESS_START -->

## Implantação por etapas

| Etapa | Direção | Média | Módulos |
|---:|---|---:|---|
{chr(10).join(stage_rows)}

{explanations}

## Evolução por módulo

| Etapa | Módulo | Escopo público | Conclusão | Estado |
|---:|---|---|---:|---|
{chr(10).join(module_rows)}

<!-- MODULE_PROGRESS_END -->

## Como o percentual é atualizado

A automação diária lê a seção `Matriz por módulo` do plano oficial de execução no repositório privado, calcula a média geral e atualiza este documento.

A publicação automática:

1. lê apenas os nomes e percentuais autorizados;
2. gera este painel público;
3. cria um commit em branch automática;
4. abre um pull request;
5. faz o merge por squash;
6. não publica pendências, dados pessoais ou segredos.

O percentual representa a evolução técnica consolidada registrada no plano oficial. Ele não significa autorização de produção, homologação regulatória ou disponibilidade comercial imediata.
"""


def replace_between(text: str, start: str, end: str, body: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"Marcadores não encontrados: {start} / {end}")
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return f"{prefix}{start}\n\n{body.rstrip()}\n\n{end}{suffix}"


def render_readme(readme: str, matrix: dict[str, int], config: dict, now: datetime) -> str:
    values = configured_values(matrix, config)
    rows: list[str] = []
    for stage in config["stages"]:
        stage_values = [matrix[slug] for slug in stage["modules"]]
        rows.append(
            f"| Etapa {stage['id']} | {stage['title']} | "
            f"{round(sum(stage_values) / len(stage_values))}% |"
        )
    body = f"""| Etapa | Direção | Evolução |
|---:|---|---:|
{chr(10).join(rows)}

**Evolução total do projeto:** **{round(sum(values) / len(values))}%**

**Módulos acompanhados:** **{len(values)}**

**Última atualização:** {now.strftime('%d/%m/%Y às %H:%M')}.

[Ver todos os módulos, etapas e percentuais](docs/modules.md)"""
    return replace_between(readme, README_START, README_END, body)


def main() -> int:
    args = arguments()
    public_root = args.public_root.resolve()
    private_root = args.private_root.resolve()
    config = json.loads(read((public_root / args.config).resolve()))
    now = datetime.now(ZoneInfo(config.get("timezone", "America/Sao_Paulo")))
    matrix = matrix_from_plan(read(private_root / "docs" / "EXECUTION_PLAN.md"))
    catalog = catalog_from_file(private_root / "config" / "module_catalog.json")

    (public_root / "docs" / "modules.md").write_text(
        render_modules(matrix, catalog, config, now),
        encoding="utf-8",
    )
    readme_path = public_root / "README.md"
    readme_path.write_text(
        render_readme(read(readme_path), matrix, config, now),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
