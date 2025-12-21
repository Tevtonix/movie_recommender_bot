from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Регистрация нового пользователя"""
    logger.info(f"Попытка регистрации пользователя: {user_data.username}")
    
    # Проверка существования пользователя
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"Пользователь {user_data.username} уже существует")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем или email уже существует"
        )
    
    # Создание нового пользователя
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"Пользователь {user_data.username} успешно зарегистрирован")
    
    # Создание токена
    access_token = create_access_token(data={"sub": new_user.username})
    
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Авторизация пользователя"""
    logger.info(f"Попытка входа пользователя: {user_data.username}")
    
    # Поиск пользователя
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа для пользователя: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    
    logger.info(f"Пользователь {user_data.username} успешно авторизован")
    
    # Создание токена
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(access_token=access_token)
