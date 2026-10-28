"""
Vercel serverless entry point for FastAPI — PATH DIAGNOSTIC
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Minimal debug app that always responds with what path Vercel actually sent
debug_app = FastAPI()
debug_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@debug_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(path: str, request: Request):
    headers = {k.decode(): v.decode() for k, v in request.scope.get("headers", [])}
    return JSONResponse({
        "url_path": request.url.path,
        "scope_path": request.scope.get("path"),
        "root_path": request.scope.get("root_path", ""),
        "path_param": path,
        "x_forwarded_host": headers.get("x-forwarded-host"),
        "x_vercel_proxied_for": headers.get("x-vercel-proxied-for"),
        "x_matched_path": headers.get("x-matched-path"),
        "x_vercel_deployment_url": headers.get("x-vercel-deployment-url"),
    })

handler = debug_app
