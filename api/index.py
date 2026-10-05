"""
Vercel serverless entry point — root-level api/ for reliable function discovery.
"""
import sys
import os

# Point to backend/ so 'from app.main import app' resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from app.main import app

handler = app
