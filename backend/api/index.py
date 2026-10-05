"""
Vercel serverless entry point for FastAPI
"""
import sys
import os
import traceback

# Use abspath to ensure we get an absolute path regardless of how __file__ is set
_this_file = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(_this_file))
sys.path.insert(0, _backend_dir)

print(f"[startup] __file__       = {__file__}")
print(f"[startup] _this_file     = {_this_file}")
print(f"[startup] _backend_dir   = {_backend_dir}")
print(f"[startup] sys.path[0]    = {sys.path[0]}")

try:
    from app.main import app as _main_app
    print("[startup] ✅ app loaded OK")

    # Add a catch-all AFTER all existing routes so it only fires when
    # nothing else matches — it will show us what path Vercel is passing.
    from fastapi import Request
    from fastapi.responses import JSONResponse

    @_main_app.api_route("/{path:path}",
                         methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
    async def _debug_catch_all(path: str, request: Request):
        return JSONResponse({
            "debug":      "catch_all_fired",
            "path_param": path,
            "url_path":   request.url.path,
            "scope_path": request.scope.get("path"),
            "root_path":  request.scope.get("root_path", ""),
            "method":     request.method,
        })

    app = _main_app
    handler = _main_app

except Exception as _e:
    _tb = traceback.format_exc()
    print(f"[startup] ❌ CRASHED:\n{_tb}")

    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware

    _err_app = FastAPI()
    _err_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )

    @_err_app.api_route("/{path:path}",
                        methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
    async def _crash_handler(path: str, request: Request):
        return JSONResponse(status_code=500, content={
            "startup_crash": str(_e),
            "traceback":     _tb,
            "file":          __file__,
            "backend_dir":   _backend_dir,
            "sys_path_0":    sys.path[0],
        })

    app = _err_app
    handler = _err_app
