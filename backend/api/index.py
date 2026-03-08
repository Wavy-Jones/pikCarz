"""
Vercel serverless entry point for FastAPI
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

# Vercel looks for either 'app' or 'handler'
handler = app
