import sys
from pathlib import Path

from fastapi import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app

app = create_module_app("services")


@app.get("/providers/{provider_id}/time-slots")
async def get_time_slots(provider_id: str, date: str):
    """
    Mock do Motor de Calendário: retorna slots de horários disponíveis
    para um prestador num dia específico.
    """
    return {
        "provider_id": provider_id,
        "date": date,
        "available_slots": ["09:00", "10:00", "11:30", "14:00", "15:30", "16:00"],
    }


@app.post("/providers/{provider_id}/reserve-slot")
async def reserve_slot(provider_id: str, request: Request, body: dict):
    """
    Mock de Reserva de Calendário. Simula a verificação de concorrência.
    """
    slot = body.get("slot")
    customer_id = body.get("customer_id")

    if not slot or not customer_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="slot e customer_id obrigatorios.")

    if slot in ["10:00", "14:00"]:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=409,
            detail=f"O horario {slot} acabou de ser reservado por outra pessoa.",
        )

    return {
        "status": "reserved",
        "provider_id": provider_id,
        "slot": slot,
        "customer_id": customer_id,
        "reservation_id": f"res-{customer_id}-{slot.replace(':', '')}",
    }
