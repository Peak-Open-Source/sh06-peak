# Adds needed modules and directories to current path for pytest tests

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../PSS_microservice')))
from src.protein import Protein
from main import app
from main import select_best_structure
