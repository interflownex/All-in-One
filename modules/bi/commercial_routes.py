from collections import defaultdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from shared.security import Actor, actor_from_headers

router = APIRouter()


@router.get("/valley/bi/commercial-insights/series")
def commercial_insights_series(
    request: Request,
    actor: Annotated[Actor, Depends(actor_from_headers)],
) -> dict[str, Any]:
    store = request.app.extra["store"]
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
    for order in store.list("orders"):
        date_str = order["created_at"][:10]
        series[date_str]["orders_total"] += 1
        if order["status"] in {
            "paid",
            "accepted",
            "in_progress",
            "delivered",
            "completed",
        }:
            series[date_str]["orders_paid"] += 1
            series[date_str]["faturamento_total"] += float(
                order.get("payload", {}).get("total_amount", 0.0)
            )
    for dispute in store.list("disputes"):
        if dispute["status"] in {"open", "under_review"}:
            series[dispute["created_at"][:10]]["disputes_opened"] += 1
    for review in store.list("reviews"):
        rating = str(review.get("payload", {}).get("rating", ""))
        if rating.isdigit():
            date_str = review["created_at"][:10]
            series[date_str]["reviews_count"] += 1
            series[date_str]["reviews_sum"] += int(rating)

    historical_series = []
    for date_str in sorted(series):
        data = series[date_str]
        reviews_count = data["reviews_count"]
        orders_total = data["orders_total"]
        historical_series.append(
            {
                "date": date_str,
                "orders_total": orders_total,
                "orders_paid": data["orders_paid"],
                "revenue_total": data["faturamento_total"],
                "conversion_rate_percent": round(
                    data["orders_paid"] / orders_total * 100, 2
                )
                if orders_total
                else 0.0,
                "disputes_opened": data["disputes_opened"],
                "average_rating": round(data["reviews_sum"] / reviews_count, 2)
                if reviews_count
                else None,
            }
        )
    return {
        "historical_series": historical_series,
        "source": "bi.commercial_insights",
        "actor": str(actor.user_id),
    }
