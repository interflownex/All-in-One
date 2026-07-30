from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from business.commercial_routes import router as commercial_router
from business.module_settings import router as module_settings_router


app = create_module_app("business")
app.include_router(commercial_router)
app.include_router(module_settings_router)
