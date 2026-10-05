"""
Vercel serverless entry point — diagnostic version
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Diagnostic wrapper - reveals what path Vercel actually passes
diag_app = FastAPI()

try:
    from app.main import app as real_app
    import_error = None
except Exception as e:
    real_app = None
    import_error = f"{type(e).__name__}: {e}"

@diag_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(path: str, request: Request):
    if real_app is None:
        return JSONResponse({
            "diagnostic": "IMPORT_FAILED",
            "error": import_error,
            "received_path": request.url.path,
            "method": request.method
        }, status_code=500)

    # Forward to real app if import succeeded
    # First show diagnostic
    return JSONResponse({
        "diagnostic": "APP_LOADED_OK",
        "received_path": request.url.path,
        "method": request.method,
        "path_param": path,
        "headers": dict(request.headers),
        "import_error": import_error
    })

handler = diag_app
