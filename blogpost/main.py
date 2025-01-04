import logging
import sys

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

sys.dont_write_bytecode = True

from blogpost.auth import auth_router
from blogpost.config import lifespan
from blogpost.posts import post_router

logger = logging.getLogger("blogpost")

app = FastAPI(lifespan=lifespan)

logger.info("Application startup completed")

app.include_router(auth_router)
app.include_router(post_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc: HTTPException):
    logger.error(f"Exception: status_code={exc.status_code}, detail={exc.detail}")
    return await http_exception_handler(request, exc)
