#!/usr/bin/env python3
"""Run the full-backend analyzer CLI from the repository root."""
from pathlib import Path
import runpy
import sys

BACKEND_DIR = Path(__file__).resolve().parent / 'securecode-backend'
sys.path.insert(0, str(BACKEND_DIR))
runpy.run_path(str(BACKEND_DIR / 'cli.py'), run_name='__main__')
