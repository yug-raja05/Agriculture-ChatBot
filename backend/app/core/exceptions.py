from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_429_TOO_MANY_REQUESTS,
)

class AgriGeniusException(Exception):
    """Base exception for AgriGenius application"""
    def __init__(self, message: str, status_code: int = HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EntityNotFoundException(AgriGeniusException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=HTTP_404_NOT_FOUND)

class UserUnauthorizedException(AgriGeniusException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=HTTP_401_UNAUTHORIZED)

class AccessForbiddenException(AgriGeniusException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=HTTP_403_FORBIDDEN)

class RateLimitExceededException(AgriGeniusException):
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(message, status_code=HTTP_429_TOO_MANY_REQUESTS)

class InvalidInputException(AgriGeniusException):
    def __init__(self, message: str = "Invalid input values"):
        super().__init__(message, status_code=HTTP_400_BAD_REQUEST)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AgriGeniusException)
    async def agrigenius_exception_handler(request: Request, exc: AgriGeniusException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.message,
                    "code": exc.__class__.__name__
                }
            }
        )
        
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "message": "Internal server error occurred.",
                    "code": "InternalServerError"
                }
            }
        )
