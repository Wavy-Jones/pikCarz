"""
Vercel ASGI entrypoint for PikCarz API (root-level deployment).

Deployed from repo root; loads FastAPI app from backend/.
The variable MUST be named 'app' for Vercel's Python runtime to detect it.
"""
import os
import sys

# Robust backend/ discovery — works whether __file__ is absolute or relative
# and whether cwd is /var/task or /var/task/api
_this_file = os.path.abspath(__file__)       # e.g. /var/task/api/index.py
_api_dir   = os.path.dirname(_this_file)     # /var/task/api
_root_dir  = os.path.dirname(_api_dir)       # /var/task

# Try paths in priority order; the first one that exists wins
for _candidate in [
    os.path.join(_root_dir, "backend"),          # /var/task/backend  (normal case)
    os.path.join(_api_dir,  "..", "backend"),     # same, via ..
    os.path.join(os.getcwd(), "backend"),         # cwd/backend fallback
    "/var/task/backend",                          # Vercel absolute fallback
]:
    _candidate = os.path.normpath(_candidate)
    if os.path.isdir(_candidate):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        break

from app.main import app  # noqa: E402  — this IS the Vercel entrypoint
