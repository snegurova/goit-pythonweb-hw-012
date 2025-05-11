from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with this email already exists"

def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "The username or password is incorrect"

def test_wrong_username_login(client):
    response = client.post("api/auth/login",
                           data={"username": "username", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "The username or password is incorrect"

def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

def test_register_conflict_email(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.send_email", Mock())
    unique_data = {"username": "conflict_test_1", "email": "unique1@example.com", "password": "12345678"}
    response = client.post("api/auth/register", json=unique_data)
    assert response.status_code == 201

    conflict_data = {
        "username": "different_username",
        "email": unique_data["email"],
        "password": "12345678"
    }
    response = client.post("api/auth/register", json=conflict_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"


def test_register_conflict_username(client, monkeypatch):
    monkeypatch.setattr("src.api.auth.send_email", Mock())
    unique_data = {"username": "conflict_test_2", "email": "unique2@example.com", "password": "12345678"}
    response = client.post("api/auth/register", json=unique_data)
    assert response.status_code == 201

    conflict_data = {
        "username": unique_data["username"],
        "email": "another_email@example.com",
        "password": "12345678"
    }
    response = client.post("api/auth/register", json=conflict_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this username already exists"