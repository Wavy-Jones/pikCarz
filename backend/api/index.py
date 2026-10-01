"""
Vercel serverless entry point for FastAPI
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

handler = app
