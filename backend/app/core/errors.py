"""
LinguaChat — Shared Error Definitions & Exception Handlers

Defines standard error response format and exception handlers for FastAPI.
All HTTP error codes and formats must match docs/api-contract.md.
"""

from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# ── Standard Error Response Builder ───────────────────────────────────────────

def error_response(code: str, message: str, details: Optional[dict] = None) -> dict:
    """
    Build a standard error response body.
    Format matches docs/api-contract.md.
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


# ── Custom Exception Classes ───────────────────────────────────────────────────

class LinguaChatException(Exception):
    """Base exception for LinguaChat application errors."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(LinguaChatException):
    def __init__(self, resource: str, identifier: str = ""):
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} not found" + (f": {identifier}" if identifier else ""),
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedError(LinguaChatException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(LinguaChatException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(LinguaChatException):
    def __init__(self, code: str, message: str):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationError(LinguaChatException):
    def __init__(self, message: str):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class TranslationError(LinguaChatException):
    def __init__(self, message: str = "All translation providers failed"):
        super().__init__(
            code="TRANSLATION_FAILED",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ── Exception Handlers ────────────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""

    @app.exception_handler(LinguaChatException)
    async def linguachat_exception_handler(
        request: Request, exc: LinguaChatException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Sanitize errors: convert non-serializable objects (e.g., ValueError)
        # to string representations for safe JSON serialization.
        safe_errors = []
        for err in exc.errors():
            safe_err = {}
            for k, v in err.items():
                if k == "ctx" and isinstance(v, dict):
                    safe_err[k] = {ck: str(cv) for ck, cv in v.items()}
                else:
                    safe_err[k] = v
            safe_errors.append(safe_err)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                "VALIDATION_ERROR",
                "Request validation failed",
                {"errors": safe_errors},
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # Never expose internal error details in production
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                "INTERNAL_SERVER_ERROR",
                "An unexpected error occurred",
            ),
        )
