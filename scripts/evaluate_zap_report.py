#!/usr/bin/env python3
"""Aplica o gate de severidade ao JSON do OWASP ZAP sem expor URLs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

RISK_LEVELS = {"informational": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def alerts_from_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for site in report.get("site", []):
        alerts.extend(
            alert for alert in site.get("alerts", []) if isinstance(alert, dict)
        )
    return alerts


def risk_code(alert: dict[str, Any]) -> int:
    raw = alert.get("riskcode", alert.get("riskCode", -1))
    try:
        return int(raw)
    except (TypeError, ValueError):
        return -1


def sanitized_summary(alerts: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(risk_code(alert) for alert in alerts)
    findings = [
        {
            "plugin_id": str(alert.get("pluginid", alert.get("pluginId", "unknown")))[
                :32
            ],
            "name": str(alert.get("name", "unnamed"))[:160],
            "risk_code": risk_code(alert),
            "risk": str(alert.get("riskdesc", alert.get("risk", "unknown"))).split(
                " ", 1
            )[0][:32],
        }
        for alert in alerts
    ]
    return {
        "scanner": "owasp-zap-full-scan",
        "contains_target_urls": False,
        "counts": {str(level): counts.get(level, 0) for level in range(5)},
        "findings": findings,
    }


def evaluate(report_path: Path, summary_path: Path, fail_at: str) -> int:
    if not report_path.is_file():
        raise FileNotFoundError(f"Relatorio ZAP ausente: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    alerts = alerts_from_report(report)
    summary_path.write_text(
        json.dumps(sanitized_summary(alerts), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    threshold = RISK_LEVELS[fail_at]
    blocking = [alert for alert in alerts if risk_code(alert) >= threshold]
    if blocking:
        print(f"Gate DAST reprovado: {len(blocking)} achado(s) {fail_at} ou superior.")
        return 1
    print(f"Gate DAST aprovado: {len(alerts)} achado(s), nenhum {fail_at} ou superior.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--fail-at", choices=tuple(RISK_LEVELS), default="high")
    args = parser.parse_args()
    return evaluate(args.report, args.summary, args.fail_at)


if __name__ == "__main__":
    raise SystemExit(main())
