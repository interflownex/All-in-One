from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from bi.commercial_routes import router as commercial_router


app = create_module_app("bi")
app.include_router(commercial_router)
