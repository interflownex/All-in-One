import sys
from collections import defaultdict
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers

app = create_module_app("bi")


@app.get("/valley/bi/commercial-insights/series")
def commercial_insights_series(
    actor: Annotated[Actor, Depends(actor_from_headers)],
) -> dict[str, Any]:
    store = app.extra["store"]
    orders = store.list("orders")
    reviews = store.list("reviews")
    disputes = store.list("disputes")

    series: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "orders_total": 0,
            "orders_paid": 0,
            "faturamento_total": 0.0,
            "disputes_opened": 0,
            "reviews_count": 0,
            "reviews_sum": 0,
        }
    )

    for order in orders:
        date_str = order["created_at"][:10]  # YYYY-MM-DD
        series[date_str]["orders_total"] += 1
        if order["status"] in {
            "paid",
            "accepted",
            "in_progress",
            "delivered",
            "completed",
        }:
            series[date_str]["orders_paid"] += 1
            payload = order.get("payload", {})
            amount = float(payload.get("total_amount", 0.0))
            series[date_str]["faturamento_total"] += amount

    for dispute in disputes:
        date_str = dispute["created_at"][:10]
        if dispute["status"] in {"open", "under_review"}:
            series[date_str]["disputes_opened"] += 1

    for review in reviews:
        date_str = review["created_at"][:10]
        payload = review.get("payload", {})
        rating = str(payload.get("rating", ""))
        if rating.isdigit():
            series[date_str]["reviews_count"] += 1
            series[date_str]["reviews_sum"] += int(rating)

    # Calculate averages and format output
    historical_series = []
    for date_str in sorted(series.keys()):
        data = series[date_str]
        avg_rating = (
            round(data["reviews_sum"] / data["reviews_count"], 2)
            if data["reviews_count"] > 0
            else None
        )
        conversion = (
            round((data["orders_paid"] / data["orders_total"]) * 100, 2)
            if data["orders_total"] > 0
            else 0.0
        )
        historical_series.append(
            {
                "date": date_str,
                "orders_total": data["orders_total"],
                "orders_paid": data["orders_paid"],
                "revenue_total": data["faturamento_total"],
                "conversion_rate_percent": conversion,
                "disputes_opened": data["disputes_opened"],
                "average_rating": avg_rating,
            }
        )

    return {
        "historical_series": historical_series,
        "source": "bi.commercial_insights",
        "actor": str(actor.user_id),
    }
