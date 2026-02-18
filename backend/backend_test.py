import os
import pytest
import requests

BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")
API = f"{BASE_URL}/api"


def test_create_contact_submission_ok():
    payload = {
        "name": "PyTest User",
        "email": "pytest.user@example.com",
        "message": "Hello from pytest! This is a test message.",
    }
    r = requests.post(f"{API}/contact", json=payload, timeout=20)
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["message"] == payload["message"]
    assert "created_at" in data


def test_create_contact_submission_invalid_email():
    payload = {"name": "Bad Email", "email": "not-an-email", "message": "hello world 123"}
    r = requests.post(f"{API}/contact", json=payload, timeout=20)
    assert r.status_code == 422


def test_recent_requires_jwt():
    r = requests.get(f"{API}/contact/recent", timeout=20)
    assert r.status_code == 401


def test_login_and_fetch_recent_with_bearer_token():
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    assert admin_email and admin_password

    login = requests.post(
        f"{API}/auth/login",
        json={"email": admin_email, "password": admin_password},
        timeout=20,
    )
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token

    recent = requests.get(
        f"{API}/contact/recent",
        headers={"Authorization": f"Bearer {token}"},
        timeout=20,
    )
    assert recent.status_code == 200
    data = recent.json()
    assert "items" in data
    assert isinstance(data["items"], list)
