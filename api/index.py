"""
Vercel ASGI entrypoint for PikCarz API (root-level deployment).
The variable MUST be named 'app' for Vercel's Python runtime to detect it.
"""
import os
import sys

# Robust backend/ discovery — works whether __file__ is absolute or relative
_this_file = os.path.abspath(__file__)
_api_dir   = os.path.dirname(_this_file)
_root_dir  = os.path.dirname(_api_dir)

for _candidate in [
    os.path.join(_root_dir, "backend"),
    os.path.join(_api_dir,  "..", "backend"),
    os.path.join(os.getcwd(), "backend"),
    "/var/task/backend",
]:
    _candidate = os.path.normpath(_candidate)
    if os.path.isdir(_candidate):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        break

from app.main import app  # noqa: E402
