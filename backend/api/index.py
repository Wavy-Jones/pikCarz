"""
Vercel serverless function entry point
This is different from app/api/ which contains route handlers
"""
from app.main import app

# Vercel expects this for serverless deployment
handler = app
