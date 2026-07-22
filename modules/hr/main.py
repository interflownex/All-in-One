import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app

app = create_module_app("hr")
