import logging
import sys

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

sys.dont_write_bytecode = True

from .auth import auth_router
from .config import lifespan
from .diary import draft_router
from .posts import post_router

logger = logging.getLogger()

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI-based API's to manage Blogs",
    terms_of_service="https://github.com/biradar8/BlogpostProject",
)

logger.info("Application startup completed")

app.include_router(auth_router, prefix="/api")
app.include_router(post_router, prefix="/api")
app.include_router(draft_router, prefix="/api")


@app.get("/")
def home():
    return {"Hello": "World"}


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc: HTTPException):
    logger.error(f"Exception: status_code={exc.status_code}, detail={exc.detail}")
    return await http_exception_handler(request, exc)
