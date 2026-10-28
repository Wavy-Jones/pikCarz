"""
Vercel serverless entry point for FastAPI
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import_error = None
try:
    from app.main import app
except Exception as e:
    import traceback
    import_error = traceback.format_exc()
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def catch_all(path: str, request: Request):
        return JSONResponse({"import_error": import_error}, status_code=500)

handler = app
