import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from backend.app.main import app
import backend.app.auth as auth_module

# 🔌 Отключаем Redis
auth_module.redis_client = MagicMock()
auth_module.redis_client.sismember.return_value = False
auth_module.redis_client.sadd.return_value = True

client = TestClient(app)

@pytest.fixture(scope="module")
def valid_user():
    return {
        "username": "validuser",
        "password": "validpass123",
        "password_repeat": "validpass123"
    }

@pytest.fixture(scope="module")
def valid_email_user():
    return {
        "email": "valid@example.com",
        "password": "validpass123",
        "password_repeat": "validpass123"
    }

def test_register_with_username(valid_user):
    response = client.post("/auth/register", json=valid_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == valid_user["username"]
    assert "id" in data

def test_register_with_email(valid_email_user):
    response = client.post("/auth/register", json=valid_email_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == valid_email_user["email"]
    assert "id" in data

def test_login_with_username(valid_user):
    login_data = {
        "username": valid_user["username"],
        "password": valid_user["password"]
    }
    response = client.post("/auth/token", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    global access_token
    access_token = data["access_token"]

def test_login_with_email(valid_email_user):
    login_data = {
        "email": valid_email_user["email"],
        "password": valid_email_user["password"]
    }
    response = client.post("/auth/token", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_verify_token():
    response = client.get(f"/auth/verify-token/{access_token}")
    assert response.status_code == 200
    assert "user_id" in response.json()

def test_logout():
    response = client.post("/auth/logout", params={"token": access_token})
    assert response.status_code == 200
    assert "успешно" in response.json()["message"]

def test_verify_blacklisted_token():
    # Теперь Redis считает токен отозванным
    auth_module.redis_client.sismember.return_value = True
    response = client.get(f"/auth/verify-token/{access_token}")
    assert response.status_code == 403
    assert "Токен отозван" in response.json()["detail"]
