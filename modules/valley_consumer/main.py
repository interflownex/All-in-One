from fastapi import FastAPI

from .innovation_round_004 import router as innovation_round_004_router

app = FastAPI(
    title="APK Valley Consumidor",
    version="4.1.0",
    description="Orquestração executável das decisões da Rodada 004 de inovação.",
)
app.include_router(innovation_round_004_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "valley-consumer", "innovation_round": "004"}
