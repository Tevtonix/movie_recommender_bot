from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
import uuid

from app.database import get_db
from app.models import User, Session, Message
from app.schemas import (
    SessionCreate, SessionResponse, MessageRequest, 
    MessageResponse, ChatHistoryResponse, MessageHistory
)
from app.auth import get_current_user
from app.bot_logic import bot

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """Создание новой сессии диалога"""
    logger.info(f"Создание новой сессии для пользователя: {current_user.username}")
    
    session_id = str(uuid.uuid4())
    new_session = Session(
        session_id=session_id,
        user_id=current_user.id
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    logger.info(f"Сессия {session_id} успешно создана")
    
    return SessionResponse(
        session_id=new_session.session_id,
        created_at=new_session.created_at
    )


@router.post("/message", response_model=MessageResponse)
async def send_message(
    message_data: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Отправка сообщения и получение ответа от бота"""
    logger.info(f"Получено сообщение от пользователя {current_user.username} в сессии {message_data.session_id}")
    
    # Проверка существования сессии
    result = await db.execute(
        select(Session).where(Session.session_id == message_data.session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        logger.error(f"Сессия {message_data.session_id} не найдена")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    # Проверка принадлежности сессии пользователю
    if session.user_id != current_user.id:
        logger.warning(f"Пользователь {current_user.username} пытается получить доступ к чужой сессии")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ к этой сессии запрещен"
        )
    
    # Сохранение сообщения пользователя
    user_message = Message(
        session_id=session.id,
        sender="user",
        text=message_data.text
    )
    db.add(user_message)
    
    # Генерация ответа бота
    bot_response_text = bot.get_response(message_data.text)
    
    # Сохранение ответа бота
    bot_message = Message(
        session_id=session.id,
        sender="bot",
        text=bot_response_text
    )
    db.add(bot_message)
    
    await db.commit()
    await db.refresh(user_message)
    
    logger.info(f"Сообщения сохранены в сессии {message_data.session_id}")
    
    return MessageResponse(
        user_message=message_data.text,
        bot_message=bot_response_text,
        timestamp=user_message.timestamp
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ChatHistoryResponse:
    """Получение истории диалога"""
    logger.info(f"Запрос истории для сессии {session_id} от пользователя {current_user.username}")
    
    # Проверка существования сессии
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.messages))
        .where(Session.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        logger.error(f"Сессия {session_id} не найдена")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    # Проверка принадлежности сессии пользователю
    if session.user_id != current_user.id:
        logger.warning(f"Пользователь {current_user.username} пытается получить доступ к чужой истории")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ к истории этой сессии запрещен"
        )
    
    # Формирование истории
    messages = [
        MessageHistory(
            sender=msg.sender,
            text=msg.text,
            timestamp=msg.timestamp
        )
        for msg in sorted(session.messages, key=lambda x: x.timestamp)
    ]
    
    logger.info(f"История сессии {session_id} успешно получена, сообщений: {len(messages)}")
    
    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages
    )
