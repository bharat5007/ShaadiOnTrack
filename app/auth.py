from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import httpx
from app.config import settings

security = HTTPBearer()


async def verify_token_with_auth_service(token: str) -> dict:
    """
    Verify token with the Auth service.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: User information from auth service
        
    Raises:
        HTTPException: If token is invalid or auth service is unreachable
    """
    try:
        async with httpx.AsyncClient(timeout=settings.AUTH_SERVICE_TIMEOUT) as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )


def decode_token_locally(token: str) -> dict:
    """
    Decode JWT token locally (fallback method).
    
    Args:
        token: JWT token to decode
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user.
    
    This function first tries to verify the token with the Auth service.
    If the Auth service is unavailable, it falls back to local token decoding.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        dict: User information
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    try:
        # Try to verify with auth service first
        user_data = await verify_token_with_auth_service(token)
        return user_data
    except HTTPException as e:
        if e.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            # Fallback to local token verification
            return decode_token_locally(token)
        raise


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        dict: Active user information
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_user_id(current_user: dict = Depends(get_current_active_user)) -> int:
    """
    Extract user ID from current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        int: User ID
        
    Raises:
        HTTPException: If user ID is not found
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    return int(user_id)