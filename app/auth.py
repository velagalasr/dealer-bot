from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from app.config import settings

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from request header
    
    Args:
        api_key: API key from X-API-Key header
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key