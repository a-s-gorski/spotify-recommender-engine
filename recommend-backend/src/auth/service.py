from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader
from src.auth.config import settings
from typing import Optional
from fastapi import HTTPException, Depends

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class AuthService:
    @staticmethod
    async def get_api_key(api_key: Optional[str] = Depends(api_key_header)):
        if api_key != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
            )
        return api_key
