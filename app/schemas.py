from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import List, Optional


class UserRegister(BaseModel):
    """Схема регистрации пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Имя пользователя не может быть пустым')
        return v.strip()

    @field_validator('password')
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Пароль не может быть пустым')
        return v


class UserLogin(BaseModel):
    """Схема входа пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"


class SessionCreate(BaseModel):
    """Схема создания сессии"""
    pass


class SessionResponse(BaseModel):
    """Схема ответа с сессией"""
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    """Схема запроса сообщения"""
    session_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1, max_length=1000)

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Текст сообщения не может быть пустым')
        return v.strip()

    @field_validator('session_id')
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('ID сессии не может быть пустым')
        return v.strip()


class MessageResponse(BaseModel):
    """Схема ответа сообщения"""
    user_message: str
    bot_message: str
    timestamp: datetime


class MessageHistory(BaseModel):
    """Схема истории сообщений"""
    sender: str
    text: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Схема ответа с историей чата"""
    session_id: str
    messages: List[MessageHistory]
