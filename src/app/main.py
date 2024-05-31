import uvicorn
from app.api.routers import healthz, hello
from app.bootstrap import handle_exceptions, lifespan, log_request_and_response
from app.settings import settings
from domain.environment.env import Env
from fastapi import APIRouter, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    lifespan=lifespan,
    debug=settings.debug,
    title="Base Code",
)

if settings.env != Env.PYTEST:
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_and_response)

app.add_middleware(BaseHTTPMiddleware, dispatch=handle_exceptions)

if settings.env != Env.PYTEST:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=[
            "Authorization",
        ],
    )

v1 = APIRouter(prefix="/api/v1")
v1.include_router(hello.router)
app.include_router(v1)

app.include_router(healthz.router)

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
