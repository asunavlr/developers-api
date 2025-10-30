import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import time

from .utils.logging import configure_logging, get_logger

load_dotenv()

app = FastAPI(title="Users API (Python)", version="1.0.0")
configure_logging()
logger = get_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)
        # Avoid logging overly large bodies; focus on essentials
        extra = {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": latency_ms,
        }
        try:
            logger.info("http_request", extra=extra)
        except Exception:
            pass
        return response


app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Uniform 422 envelope
    return JSONResponse(
        status_code=422,
        content={
            "message": "Erro de validação",
            "errors": exc.errors(),
            "path": request.url.path,
        },
    )

from .routers.auth import router as auth_router  # noqa: E402
from .routers.users import router as users_router  # noqa: E402

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])

@app.get("/")
def root():
    return {"status": "ok", "service": "Users API (Python)", "version": "1.0.0"}