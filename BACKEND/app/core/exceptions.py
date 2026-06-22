"""
Exception handlers centralizados — RFC 7807 (Problem Details for HTTP APIs).

Todos los errores del backend pasan por acá, garantizando un formato de respuesta
consistente: { "type", "title", "status", "detail", "instance", "errors" }.
"""

import logging

from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Errores 4xx y 5xx lanzados con HTTPException desde services/routers."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": exc.detail if isinstance(exc.detail, str) else "Error",
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url),
        },
        headers=getattr(exc, "headers", None) or {},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Errores 422 cuando el body/query/params no pasan la validación Pydantic."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(
        "Validation error | %s %s | %d errores",
        request.method, request.url.path, len(errors),
    )

    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": "Unprocessable Entity",
            "status": 422,
            "detail": "Error de validación en los datos enviados",
            "instance": str(request.url),
            "errors": errors,
        },
    )
