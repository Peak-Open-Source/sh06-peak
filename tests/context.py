# Adds needed modules and directories to current path for pytest tests

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../PSS_microservice')))
import src.models as models  # noqa:F401,E402
from src.protein import Protein  # noqa:F401,E402
from main import app  # noqa:F401,E402
from src.helpers import select_best_structure  # noqa:F401,E402
