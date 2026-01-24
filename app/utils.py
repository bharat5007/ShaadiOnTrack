# utils/auth.py
import base64
import json
from datetime import datetime, timezone
from functools import wraps
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException, status
import jwt
from app.config import settings


class SharedContext(BaseModel):
    user_id: int
    phone: str
    email: str
    roles: list
    is_active: bool


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    user_id: int
    role: str


def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification (main service trusts auth service)."""
    try:
        payload_segment = token.split('.')[1]
        padding = 4 - len(payload_segment) % 4
        if padding != 4:
            payload_segment += '=' * padding
        decoded = base64.urlsafe_b64decode(payload_segment)
        return json.loads(decoded)
    except Exception:
        return {}


def is_token_expired(token: str) -> bool:
    """Check if access token is expired."""
    payload = decode_jwt_payload(token)
    exp = payload.get('exp')
    if not exp:
        return True
    return datetime.now(timezone.utc).timestamp() > exp


def decode_shared_context(encoded_context: str) -> Optional[SharedContext]:
    """Decode base64 encoded shared context from header."""
    if not encoded_context:
        return None
    
    # Remove any accidental Bearer prefix
    if encoded_context.startswith('Bearer '):
        encoded_context = encoded_context[7:].strip()
    
    try:
        # Decode and verify JWT signature
        payload = jwt.decode(
            encoded_context,
            settings.SHARED_CONTEXT_SECRET,
            algorithms="HS256"
        )
                
        # Verify token type and issuer for additional security
        if payload.get('typ') != 'shared-context' or payload.get('iss') != 'sot-auth':
            print(f"ERROR: Invalid token type or issuer. typ={payload.get('typ')}, iss={payload.get('iss')}")
            return None
        
        # Map fields from auth service JWT to SharedContext
        # Auth sends: uid, email, phone, role
        # We need: user_id, username, email, role, is_active
        shared_data = {
            'user_id': payload.get('uid'),
            'phone': payload.get('phone'),
            'email': payload.get('email'),
            'roles': payload.get('roles'),
            'is_active': True  # Auth service doesn't send this, default to True
        }
        
        return SharedContext(**shared_data)
    except Exception as e:
        # Log the error for debugging (remove in production)
        print(f"Error decoding shared context: {e}")


def require_auth(func):
    """Decorator to require valid authentication on routes."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Extract Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header[7:]
        
        # Check token expiration
        if is_token_expired(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired"
            )
        
        # Extract shared context
        context_header = request.headers.get('X-Shared-Context', '')
        if not context_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing shared context"
            )
        
        shared_context = decode_shared_context(context_header)
        if not shared_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid shared context"
            )
        
        # Attach to request state for use in route
        request.state.user = shared_context
        request.state.token_payload = decode_jwt_payload(token)
        
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_role(*allowed_roles: str):
    """Decorator to require specific roles."""
    def decorator(func):
        @wraps(func)
        @require_auth
        async def wrapper(request: Request, *args, **kwargs):
            user: SharedContext = request.state.user
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator