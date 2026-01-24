from app.config import settings
from fastapi import HTTPException
import httpx
import logging
import base64
import uuid
import jwt

logger = logging.getLogger(__name__)

class AuthServiceClient:
    
    @classmethod
    def _generate_service_token(cls) -> str:
        """Create a simple service-to-service JWT from env secret."""
        secret = (settings.AUTH_SERVICE_TOKEN or "").strip()
        if not secret:
            raise RuntimeError("AUTH_SERVICE_TOKEN is not configured")

        return jwt.encode({"service": settings.AUTH_SERVICE_TOKEN}, secret, algorithm="HS256")
    
    @staticmethod
    def _extract_error_message(resp: httpx.Response) -> str:
        # Typical FastAPI errors:
        # 1) {"detail": "some error"}
        # 2) {"detail": [{"loc": ..., "msg": "...", "type": "..."}]}
        # Or custom: {"message": "..."} / {"error": "..."}
        try:
            data = resp.json()
            if isinstance(data, dict):
                detail = data.get("detail") or data.get("message") or data.get("error")
                if isinstance(detail, list) and detail:
                    # pydantic validation error list -> use first msg if present
                    first = detail[0]
                    if isinstance(first, dict) and "msg" in first:
                        return str(first["msg"])
                    return str(first)
                if detail:
                    return str(detail)
            elif isinstance(data, list) and data:
                return str(data[0])
        except ValueError:
            pass

        return (resp.text or "").strip()[:500] or f"Auth service returned {resp.status_code}"
    
    @classmethod
    async def update_vendor_role(cls, payload):
        token = cls._generate_service_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with httpx.AsyncClient(timeout=settings.AUTH_SERVICE_TIMEOUT) as client:
            path = f"{settings.AUTH_SERVICE_URL}/api/v1/auth/add-vendor-role"
            auth_response = await client.post(path,json=payload, headers=headers)
                
            if not auth_response.is_success:
                msg = cls._extract_error_message(auth_response)
                raise HTTPException(status_code=auth_response.status_code, detail=f"Unable to update role: {msg}")