import logging
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger("ace_ai")


def api_error(code: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"error": code, "message": message})


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict) and "error" in detail and "message" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": "http_error", "message": str(detail)})


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    message = errors[0].get("msg", "Validation error") if errors else "Validation error"
    logger.error("Request validation failed", exc_info=exc, extra={"path": request.url.path})
    return JSONResponse(status_code=422, content={"error": "validation_error", "message": message})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", exc_info=exc, extra={"path": request.url.path})
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_error", "message": "An unexpected error occurred."},
    )
