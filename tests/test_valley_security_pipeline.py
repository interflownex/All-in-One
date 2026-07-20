from __future__ import annotations

import json
from pathlib import Path

from scripts.evaluate_zap_report import evaluate

ROOT = Path(__file__).resolve().parents[1]


def _report(risk_code: int) -> dict:
    return {
        "site": [
            {
                "@name": "http://sensitive-target.invalid",
                "alerts": [
                    {
                        "pluginid": "10001",
                        "name": "Synthetic finding",
                        "riskcode": str(risk_code),
                        "riskdesc": "High (Medium)",
                        "instances": [
                            {"uri": "http://sensitive-target.invalid/private"}
                        ],
                    }
                ],
            }
        ]
    }


def test_zap_gate_blocks_high_findings_and_sanitizes_urls(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    summary = tmp_path / "summary.json"
    report.write_text(json.dumps(_report(3)), encoding="utf-8")

    assert evaluate(report, summary, "high") == 1
    rendered = summary.read_text(encoding="utf-8")
    assert "sensitive-target" not in rendered
    assert json.loads(rendered)["contains_target_urls"] is False


def test_zap_gate_accepts_medium_and_reports_counts(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    summary = tmp_path / "summary.json"
    report.write_text(json.dumps(_report(2)), encoding="utf-8")

    assert evaluate(report, summary, "high") == 0
    assert json.loads(summary.read_text())["counts"]["2"] == 1


def test_security_workflows_cover_android_sast_sca_and_active_dast() -> None:
    security = (ROOT / ".github" / "workflows" / "security.yml").read_text()
    dast = (ROOT / ".github" / "workflows" / "valley-dast.yml").read_text()
    policy = json.loads(
        (ROOT / "config" / "security" / "valley_dast_policy.json").read_text()
    )

    assert "github/codeql-action/init@v4" in security
    assert "languages: java-kotlin" in security
    assert "gradle/actions/dependency-submission@v6" in security
    assert "zaproxy/action-full-scan@v0.13.0" in dast
    assert 'cmd_options: "-a -m 2 -T 5"' in dast
    assert "--fail-at high" in dast
    assert policy["active_scan"] is True
    assert policy["production_scan_allowed"] is False
    assert policy["pentest_equivalence"] is False
