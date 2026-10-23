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


def _humanize_validation_msg(msg: str) -> str:
    replacements = [
        ("Field required", "Este campo es obligatorio"),
        ("value is not a valid email address", "Email inválido"),
        ("String should have at least", "Texto demasiado corto"),
        ("String should have at most", "Texto demasiado largo"),
        ("Input should be greater than or equal to", "El valor es demasiado bajo"),
        ("Input should be less than or equal to", "El valor es demasiado alto"),
        ("value is not a valid integer", "Debe ser un número entero"),
        ("value is not a valid float", "Debe ser un número"),
        ("Input should be a valid dictionary", "Formato de datos inválido"),
        ("Input should be a valid list", "Formato de lista inválido"),
    ]
    for en, es in replacements:
        if en in msg:
            return es
    return msg


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
            "message": _humanize_validation_msg(error["msg"]),
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
            "title": "Datos inválidos",
            "status": 422,
            "detail": "Revisá los datos del formulario",
            "instance": str(request.url),
            "errors": errors,
        },
    )
