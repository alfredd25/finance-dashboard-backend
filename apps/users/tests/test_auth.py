import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@zorvyn.com",
        password="StrongPass123!",
        role="admin",
        is_active=True,
    )


@pytest.fixture
def viewer_user(db):
    return User.objects.create_user(
        email="viewer@zorvyn.com",
        password="StrongPass123!",
        role="viewer",
        is_active=True,
    )


@pytest.fixture
def analyst_user(db):
    return User.objects.create_user(
        email="analyst@zorvyn.com",
        password="StrongPass123!",
        role="analyst",
        is_active=True,
    )


def auth_client(client, user):
    response = client.post(reverse("auth-login"), {
        "email": user.email,
        "password": "StrongPass123!",
    }, format="json")
    token = response.data["data"]["tokens"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
def test_register_success(client):
    response = client.post(reverse("auth-register"), {
        "email": "newuser@zorvyn.com",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
        "first_name": "New",
        "last_name": "User",
    }, format="json")
    assert response.status_code == 201
    assert response.data["success"] is True
    assert "tokens" in response.data["data"]


@pytest.mark.django_db
def test_register_password_mismatch(client):
    response = client.post(reverse("auth-register"), {
        "email": "newuser@zorvyn.com",
        "password": "StrongPass123!",
        "password_confirm": "WrongPass123!",
    }, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_register_duplicate_email(client, viewer_user):
    response = client.post(reverse("auth-register"), {
        "email": viewer_user.email,
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
    }, format="json")
    assert response.status_code == 400



@pytest.mark.django_db
def test_login_success(client, viewer_user):
    response = client.post(reverse("auth-login"), {
        "email": viewer_user.email,
        "password": "StrongPass123!",
    }, format="json")
    assert response.status_code == 200
    assert "access" in response.data["data"]["tokens"]
    assert "refresh" in response.data["data"]["tokens"]


@pytest.mark.django_db
def test_login_wrong_password(client, viewer_user):
    response = client.post(reverse("auth-login"), {
        "email": viewer_user.email,
        "password": "WrongPassword!",
    }, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_inactive_user(client, db):
    user = User.objects.create_user(
        email="inactive@zorvyn.com",
        password="StrongPass123!",
        is_active=False,
    )
    response = client.post(reverse("auth-login"), {
        "email": user.email,
        "password": "StrongPass123!",
    }, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_logout_success(client, viewer_user):
    login = client.post(reverse("auth-login"), {
        "email": viewer_user.email,
        "password": "StrongPass123!",
    }, format="json")
    refresh = login.data["data"]["tokens"]["refresh"]
    access = login.data["data"]["tokens"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.post(reverse("auth-logout"), {"refresh": refresh}, format="json")
    assert response.status_code == 200
    assert response.data["success"] is True


@pytest.mark.django_db
def test_me_returns_current_user(client, analyst_user):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("user-me"))
    assert response.status_code == 200
    assert response.data["data"]["email"] == analyst_user.email
    assert response.data["data"]["role"] == "analyst"


@pytest.mark.django_db
def test_me_unauthenticated(client):
    response = client.get(reverse("user-me"))
    assert response.status_code == 401