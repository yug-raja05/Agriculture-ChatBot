import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Store requests as: client_ip -> list of timestamps
        self.request_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Filter timestamps older than rate limit period
        self.request_records[client_ip] = [
            t for t in self.request_records[client_ip]
            if now - t < settings.RATE_LIMIT_PERIOD
        ]
        
        # Check if rate limit is exceeded
        if len(self.request_records[client_ip]) >= settings.RATE_LIMIT_CALLS:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "message": "Too many requests. Please try again later.",
                        "code": "RateLimitExceeded"
                    }
                }
            )
            
        # Record request timestamp
        self.request_records[client_ip].append(now)
        
        response = await call_next(request)
        return response
