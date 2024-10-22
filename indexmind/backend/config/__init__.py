import os
from pathlib import Path

BACKEND_PATH = Path(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')))
SRC_PATH = BACKEND_PATH / "src"


from .main_config import Settings

settings = Settings()