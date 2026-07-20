from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from uuid import UUID
from config.database_config import get_session
from config.settings import settings
from backend.services.user_service import UserService
from slowapi import Limiter
from slowapi.util import get_remote_address

security = HTTPBearer()

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_service = UserService(session)
    user = await user_service.get_by_id(UUID(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


async def get_current_tenant(request: Request, current_user=Depends(get_current_user)):
    """Extract tenant context for multi-tenant support."""
    if not settings.multi_tenant_enabled:
        return None
    tenant_id = current_user.tenant_id
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-ID", settings.default_tenant)
    return tenant_id
