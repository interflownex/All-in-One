from fastapi import FastAPI

from .innovation_round_004 import router as innovation_round_004_router
from .innovation_round_005 import router as innovation_round_005_router

app = FastAPI(
    title="APK Valley Consumidor",
    version="5.1.0",
    description="Verticais executáveis das Rodadas 004 e 005 de inovação.",
)
app.include_router(innovation_round_004_router)
app.include_router(innovation_round_005_router)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "app": "valley-consumer",
        "innovation_rounds": ["004", "005"],
        "round_005_feature_flags_default": "off",
    }
