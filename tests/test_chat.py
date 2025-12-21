import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_session(auth_client: tuple[AsyncClient, str]):
    """Тест создания сессии"""
    client, token = auth_client
    
    response = await client.post(
        "/chat/session",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_send_message(auth_client: tuple[AsyncClient, str]):
    """Тест отправки сообщения (включая сохранение обоих сообщений)"""
    client, token = auth_client
    
    # Создание сессии
    session_response = await client.post(
        "/chat/session",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    session_id = session_response.json()["session_id"]
    
    # Отправка сообщения
    message_response = await client.post(
        "/chat/message",
        json={"session_id": session_id, "text": "Привет"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert message_response.status_code == 200
    data = message_response.json()
    assert data["user_message"] == "Привет"
    assert "bot_message" in data
    assert len(data["bot_message"]) > 0
    
    # Проверка истории
    history_response = await client.get(
        f"/chat/history/{session_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history["messages"]) == 2  # Сообщение пользователя и бота
    assert history["messages"][0]["sender"] == "user"
    assert history["messages"][0]["text"] == "Привет"
    assert history["messages"][1]["sender"] == "bot"


@pytest.mark.asyncio
async def test_get_chat_history(auth_client: tuple[AsyncClient, str]):
    """Тест получения истории переписки"""
    client, token = auth_client
    
    # Создание сессии
    session_response = await client.post(
        "/chat/session",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    session_id = session_response.json()["session_id"]
    
    # Отправка нескольких сообщений
    messages = ["Привет", "Покажи комедии", "А боевики?"]
    for msg in messages:
        await client.post(
            "/chat/message",
            json={"session_id": session_id, "text": msg},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Получение истории
    response = await client.get(
        f"/chat/history/{session_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 6  # 3 пользовательских + 3 от бота


@pytest.mark.asyncio
async def test_invalid_session_id(auth_client: tuple[AsyncClient, str]):
    """Тест обработки несуществующей сессии"""
    client, token = auth_client
    
    response = await client.post(
        "/chat/message",
        json={"session_id": "invalid-id", "text": "Тест"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]


@pytest.mark.asyncio
async def test_empty_message(auth_client: tuple[AsyncClient, str]):
    """Тест обработки пустого сообщения"""
    client, token = auth_client
    
    # Создание сессии
    session_response = await client.post(
        "/chat/session",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    session_id = session_response.json()["session_id"]
    
    # Попытка отправить пустое сообщение
    response = await client.post(
        "/chat/message",
        json={"session_id": session_id, "text": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422  # Validation error
