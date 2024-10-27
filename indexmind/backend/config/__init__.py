import os
from pathlib import Path

BACKEND_PATH = Path(__file__).resolve().parent.parent
SRC_PATH = BACKEND_PATH / "src"


from .app import settings