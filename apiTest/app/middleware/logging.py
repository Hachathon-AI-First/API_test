import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        # In a real legacy app this might be printed or use a basic logger
        print(f"Request: {request.method} {request.url.path} - Time: {process_time:.4f}s")
        return response
