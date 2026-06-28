import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from backend.models.user import User
from backend.utils.logger import get_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger("user_service")


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, username: str, password: str, full_name: str | None = None) -> User:
        hashed = pwd_context.hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed,
            full_name=full_name,
        )
        self.session.add(user)
        await self.session.flush()
        logger.info(f"Created user {user.id}")
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.get_by_email(email)
        if user and pwd_context.verify(password, user.hashed_password):
            return user
        return None

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())
