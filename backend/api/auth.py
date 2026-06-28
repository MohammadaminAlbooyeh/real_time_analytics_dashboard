from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from jose import jwt
from config.settings import settings
from backend.api.dependencies import get_db
from backend.api.schemas import UserCreate, UserResponse, TokenResponse, LoginRequest
from backend.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def create_access_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expires}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=UserResponse)
async def register(body: UserCreate, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    existing = await service.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing = await service.get_by_username(body.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = await service.create_user(
        email=body.email, username=body.username,
        password=body.password, full_name=body.full_name,
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    user = await service.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)
