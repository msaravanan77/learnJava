"""
Authentication and Authorization Middleware
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import time


security = HTTPBearer()


class AuthMiddleware:
    """JWT-based authentication middleware"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, user_id: str, workspace_id: str, expires_in: int = 3600) -> str:
        """
        Create JWT token

        Args:
            user_id: User identifier
            workspace_id: Workspace identifier
            expires_in: Token expiration in seconds

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "exp": time.time() + expires_in,
            "iat": time.time()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        """
        Verify JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check expiration
            if payload.get("exp", 0) < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )

            return payload
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )

    async def authenticate(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """
        Authenticate request using JWT token

        Args:
            credentials: HTTP bearer credentials

        Returns:
            Decoded token payload
        """
        return self.verify_token(credentials.credentials)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {user_id: [(timestamp, count)]}

    async def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit

        Args:
            user_id: User identifier

        Returns:
            True if within limits, False if exceeded

        Raises:
            HTTPException: If rate limit exceeded
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Clean up old entries
        if user_id in self.requests:
            self.requests[user_id] = [
                (ts, count) for ts, count in self.requests[user_id]
                if ts > window_start
            ]
        else:
            self.requests[user_id] = []

        # Count requests in current window
        total_requests = sum(count for _, count in self.requests[user_id])

        if total_requests >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds"
            )

        # Add current request
        self.requests[user_id].append((current_time, 1))
        return True
