"""
Vercel ASGI entrypoint for PikCarz API (root-level deployment).

Deployed from repo root; loads FastAPI app from backend/.
The variable MUST be named 'app' for Vercel's Python runtime to detect it.
"""
import os
import sys

# __file__ is repo_root/api/index.py at runtime.
# We need repo_root/backend/ on sys.path so 'from app.main import app' works.
_here = os.path.dirname(os.path.abspath(__file__))   # repo_root/api/
_root = os.path.dirname(_here)                        # repo_root/
_backend = os.path.join(_root, "backend")             # repo_root/backend/
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app  # noqa: E402  — this IS the Vercel entrypoint
