import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from business.module_settings import router as module_settings_router
from shared.runtime import create_module_app

app = create_module_app("business")
app.include_router(module_settings_router)
