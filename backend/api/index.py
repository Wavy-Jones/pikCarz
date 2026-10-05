"""
Vercel serverless entry point for FastAPI
"""
import sys
from pathlib import Path

# Insert at position 0 so our app.* always takes priority over any
# installed package that might also be named 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

handler = app
