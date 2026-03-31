from fastapi import Request, HTTPException, status
import time
from collections import defaultdict

# Simple in-memory rate limiter
# Dictionary to store request counts: {ip: [timestamp1, timestamp2, ...]}
_request_counts = defaultdict(list)

class RateLimiter:
    def __init__(self, limit: int = 5, window: int = 60):
        self.limit = limit
        self.window = window

    async def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        # Remove timestamps older than the window
        _request_counts[client_ip] = [t for t in _request_counts[client_ip] if now - t < self.window]
        
        if len(_request_counts[client_ip]) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        
        _request_counts[client_ip].append(now)
        return True
