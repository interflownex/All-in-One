import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "pendencias" / "tecnico" / "rodada-002"
DATA = SOURCE_DIR / "rodada_002_ideias.json"
GENERATOR = SOURCE_DIR / "generate_round_002_decisions.py"
STATUSES = {"approve", "study", "postpone", "reject", "reject_final"}


def load_generator():
    spec = importlib.util.spec_from_file_location("round_002_generator", GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_round_002_structured_contract() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    ideas = payload["ideas"]
    assert payload["round"] == "002"
    assert payload["module_count"] == 24
    assert payload["forbidden_modules"] == ["vision"]
    assert [item["id"] for item in ideas] == [f"R2-{n:03d}" for n in range(1, 25)]
    assert len({item["module"].casefold() for item in ideas}) == 24
    assert all(item["module"].casefold() != "vision" for item in ideas)


def test_generator_builds_complete_standalone_html(tmp_path: Path) -> None:
    output = tmp_path / "round-002.html"
    load_generator().generate(DATA, output)
    html = output.read_text(encoding="utf-8")
    embedded = re.search(r'<script id="source" type="application/json">(.*?)</script>', html, re.S)
    assert embedded and json.loads(embedded.group(1))["module_count"] == 24
    assert set(re.findall(r"(approve|study|postpone|reject|reject_final):\[", html)) == STATUSES
    assert "IDEAS.map" in html
    assert 'type="radio"' in html
    assert "<textarea" in html
    assert html.count('id="save"') == 1
    assert "localStorage" in html
    assert "function pdf(s)" in html
    assert "/Count 25" in html
    assert "forbiddenModules:['vision']" in html
    assert "Selecione uma decisão nas ${missing.length} ideias ainda pendentes." in html
