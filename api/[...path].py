"""
This file exists only to satisfy Vercel's build scan.
All routing is handled by api/index.py via vercel.json routes.
This module re-exports the same diagnostic/real app so that
whichever file Vercel actually invokes, the right handler runs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from index import app  # noqa: F401  re-export
