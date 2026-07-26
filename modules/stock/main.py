import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import Header, HTTPException
from pydantic import BaseModel, Field
from shared.runtime import create_module_app
from shared.units_tax import ConversionRule, convert_quantity
from stock.integrations import router as integrations_router

app = create_module_app("stock")
app.include_router(integrations_router)


class UnitConversionRequest(BaseModel):
    quantity: str = Field(min_length=1, max_length=80)
    multiplier: str = Field(min_length=1, max_length=80)
    divisor: str = Field(min_length=1, max_length=80)
    precision: int = Field(ge=0, le=12)
    rounding_mode: str
    source_dimension: str = Field(min_length=1, max_length=40)
    target_dimension: str = Field(min_length=1, max_length=40)
    effective_from: datetime
    effective_to: datetime | None = None
    approved: bool
    density: str | None = Field(default=None, max_length=80)


@app.post("/calculations/unit-conversion")
def calculate_unit_conversion(
    body: UnitConversionRequest,
    x_actor_user_id: str = Header(..., alias="X-Actor-User-Id"),
) -> dict[str, str]:
    """Converte quantidade no backend sem usar ponto flutuante binario."""
    try:
        result = convert_quantity(
            body.quantity,
            ConversionRule(**body.model_dump(exclude={"quantity"})),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return {
        "quantity": body.quantity,
        "converted_quantity": format(result, "f"),
        "rounding_mode": body.rounding_mode,
        "calculated_by": x_actor_user_id,
    }
