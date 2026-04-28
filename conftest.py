"""Pytest config — adds repo root to sys.path so `from src.mcp_server...` works
without installing the package. The repo has no pyproject.toml yet (Module 1
shipped with a flat layout), and pytest's autodiscovery places test imports
relative to the test file's directory, not the repo root.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
