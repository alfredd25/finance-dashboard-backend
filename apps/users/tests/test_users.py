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


def auth_client(client, user):
    response = client.post(reverse("auth-login"), {
        "email": user.email,
        "password": "StrongPass123!",
    }, format="json")
    token = response.data["data"]["tokens"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client



@pytest.mark.django_db
def test_admin_can_list_users(client, admin_user):
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("user-list"))
    assert response.status_code == 200
    assert response.data["success"] is True


@pytest.mark.django_db
def test_viewer_cannot_list_users(client, viewer_user):
    authed = auth_client(client, viewer_user)
    response = authed.get(reverse("user-list"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_unauthenticated_cannot_list_users(client):
    response = client.get(reverse("user-list"))
    assert response.status_code == 401



@pytest.mark.django_db
def test_admin_can_update_user_role(client, admin_user, viewer_user):
    authed = auth_client(client, admin_user)
    response = authed.patch(
        reverse("user-detail", kwargs={"pk": viewer_user.id}),
        {"role": "analyst"},
        format="json",
    )
    assert response.status_code == 200
    viewer_user.refresh_from_db()
    assert viewer_user.role == "analyst"


@pytest.mark.django_db
def test_viewer_cannot_update_user(client, admin_user, viewer_user):
    authed = auth_client(client, viewer_user)
    response = authed.patch(
        reverse("user-detail", kwargs={"pk": admin_user.id}),
        {"role": "viewer"},
        format="json",
    )
    assert response.status_code == 403



@pytest.mark.django_db
def test_admin_can_delete_user(client, admin_user, viewer_user):
    authed = auth_client(client, admin_user)
    response = authed.delete(
        reverse("user-detail", kwargs={"pk": viewer_user.id})
    )
    assert response.status_code == 204
    assert not User.objects.filter(id=viewer_user.id).exists()


@pytest.mark.django_db
def test_admin_cannot_delete_self(client, admin_user):
    authed = auth_client(client, admin_user)
    response = authed.delete(
        reverse("user-detail", kwargs={"pk": admin_user.id})
    )
    assert response.status_code == 400