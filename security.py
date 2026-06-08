"""
Security utilities for Answer Evaluation System.
Includes rate limiting, authentication, and input validation.
"""

import time
import hashlib
import hmac
from typing import Optional, Dict, List, Callable
from functools import wraps
from datetime import datetime, timedelta

from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed under rate limit."""
        now = time.time()
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.window_seconds
            ]
        else:
            self.requests[key] = []
        
        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Record request
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for a key."""
        now = time.time()
        
        if key in self.requests:
            recent_requests = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.window_seconds
            ]
            return max(0, self.max_requests - len(recent_requests))
        
        return self.max_requests
    
    def get_reset_time(self, key: str) -> Optional[float]:
        """Get time when rate limit resets."""
        if key not in self.requests or not self.requests[key]:
            return None
        
        oldest_request = min(self.requests[key])
        reset_time = oldest_request + self.window_seconds
        return reset_time


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, only trusting X-Forwarded-For from known proxies."""
    # Only trust X-Forwarded-For if the direct client is a known private/loopback address
    direct_ip = request.client.host if request.client else None
    _private_prefixes = ("127.", "10.", "172.16.", "172.17.", "172.18.", "172.19.",
                         "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                         "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                         "172.30.", "172.31.", "192.168.", "::1")
    is_trusted_proxy = direct_ip and (direct_ip.startswith(_private_prefixes))
    if is_trusted_proxy:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return direct_ip or "unknown"


def rate_limit():
    """Decorator/dependency for rate limiting."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = get_client_ip(request)
            
            if not rate_limiter.is_allowed(client_ip):
                reset_time = rate_limiter.get_reset_time(client_ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={
                        "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time)) if reset_time else "0"
                    }
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key if configured."""
    if not settings.API_KEY:
        # No API key required
        return None
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Use constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(credentials.credentials, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return credentials.credentials


class FileValidator:
    """Validates uploaded files."""
    
    @staticmethod
    def validate_file_size(content: bytes, max_size: int = None) -> None:
        """Validate file size."""
        max_size = max_size or settings.MAX_UPLOAD_SIZE
        
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {max_size / (1024 * 1024):.1f}MB"
            )
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str] = None) -> None:
        """Validate file extension."""
        allowed_extensions = allowed_extensions or settings.allowed_extensions_list
        
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        allowed_exts = [e.lstrip('.').lower() for e in allowed_extensions]
        
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension '.{ext}'. Allowed: {', '.join(allowed_extensions)}"
            )
    
    @staticmethod
    def validate_file_type(content: bytes, expected_types: List[str] = None) -> bool:
        """Validate file type by checking magic bytes."""
        # PDF magic bytes
        if content.startswith(b'%PDF'):
            return True
        # PNG magic bytes
        if content.startswith(b'\x89PNG'):
            return True
        # JPEG magic bytes
        if content.startswith(b'\xff\xd8\xff'):
            return True
        # Text files (UTF-8 BOM or plain text)
        if content.startswith(b'\xef\xbb\xbf') or not any(b > 127 for b in content[:100]):
            return True
        
        return False


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize input text."""
    if not isinstance(text, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input must be a string"
        )
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Strip whitespace
    text = text.strip()
    
    return text


def generate_secure_id(data: str) -> str:
    """Generate a secure hash ID for data."""
    return hashlib.sha256(f"{data}{settings.SECRET_KEY}".encode()).hexdigest()[:16]
