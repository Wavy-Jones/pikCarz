"""
PikCarz API — Vercel serverless entry point.

Vercel's file-based routing (no custom 'routes') calls this file for every
/api/** request and sets scope["path"] to the ORIGINAL requested URL, so
FastAPI can match routes normally without any path-rewriting middleware.
"""
import sys
import os

# Add backend/ to the Python path so `from app.main import app` works.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

from app.main import app  # noqa: F401  — Vercel looks for `app`
