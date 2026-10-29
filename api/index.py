"""
Vercel serverless entry point for PikCarz API.

This file lives at api/index.py (the root api/ directory) so Vercel can
auto-detect it and serve it at /api/index.  vercel.json rewrites every
/api/* request here.

Vercel's Python ASGI runtime preserves the original request path in
scope["path"] (e.g. /api/auth/login), so FastAPI receives the real URL
and routes normally — no path-recovery gymnastics needed.
"""
import sys
import os

# Add backend/ to sys.path so  `from app.X import ...`  resolves correctly.
_backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app as handler  # noqa: E402  (Vercel reads this name)
