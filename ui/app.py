"""Thin launcher so both `streamlit run app.py` and `streamlit run ui/app.py` work."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
