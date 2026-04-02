import pytest
import datetime
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.finance.models import Transaction


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
def analyst_user(db):
    return User.objects.create_user(
        email="analyst@zorvyn.com",
        password="StrongPass123!",
        role="analyst",
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
def seed_transactions(db, admin_user):
    today = datetime.date.today()
    Transaction.objects.bulk_create([
        Transaction(amount="3000.00", type="income",  category="salary",    date=today,                              created_by=admin_user),
        Transaction(amount="500.00",  type="income",  category="freelance", date=today,                              created_by=admin_user),
        Transaction(amount="1200.00", type="expense", category="rent",      date=today,                              created_by=admin_user),
        Transaction(amount="200.00",  type="expense", category="groceries", date=today - datetime.timedelta(days=5), created_by=admin_user),
        Transaction(amount="150.00",  type="expense", category="transport", date=today - datetime.timedelta(days=10),created_by=admin_user),
    ])


def auth_client(client, user):
    response = client.post(reverse("auth-login"), {
        "email": user.email,
        "password": "StrongPass123!",
    }, format="json")
    token = response.data["data"]["tokens"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client



@pytest.mark.django_db
def test_summary_correct_totals(client, admin_user, seed_transactions):
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("dashboard-summary"))
    assert response.status_code == 200
    data = response.data["data"]
    assert float(data["total_income"]) == 3500.00
    assert float(data["total_expenses"]) == 1550.00
    assert float(data["net_balance"]) == 1950.00
    assert data["total_transactions"] == 5


@pytest.mark.django_db
def test_summary_empty_database(client, admin_user):
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("dashboard-summary"))
    assert response.status_code == 200
    data = response.data["data"]
    assert float(data["total_income"]) == 0
    assert float(data["total_expenses"]) == 0
    assert float(data["net_balance"]) == 0


@pytest.mark.django_db
def test_viewer_can_access_summary(client, viewer_user, seed_transactions):
    authed = auth_client(client, viewer_user)
    response = authed.get(reverse("dashboard-summary"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_access_summary(client):
    response = client.get(reverse("dashboard-summary"))
    assert response.status_code == 401



@pytest.mark.django_db
def test_category_breakdown_structure(client, analyst_user, seed_transactions):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-categories"))
    assert response.status_code == 200
    data = response.data["data"]
    assert isinstance(data, list)
    categories = [d["category"] for d in data]
    assert "salary" in categories
    assert "rent" in categories


@pytest.mark.django_db
def test_viewer_cannot_access_categories(client, viewer_user):
    authed = auth_client(client, viewer_user)
    response = authed.get(reverse("dashboard-categories"))
    assert response.status_code == 403



@pytest.mark.django_db
def test_monthly_trends_returns_data(client, analyst_user, seed_transactions):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-monthly"))
    assert response.status_code == 200
    assert isinstance(response.data["data"], list)


@pytest.mark.django_db
def test_monthly_trends_invalid_param(client, analyst_user):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-monthly"), {"months": "99"})
    assert response.status_code == 400


@pytest.mark.django_db
def test_monthly_trends_custom_range(client, analyst_user, seed_transactions):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-monthly"), {"months": "3"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_weekly_trends_returns_data(client, analyst_user, seed_transactions):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-weekly"))
    assert response.status_code == 200
    assert isinstance(response.data["data"], list)


@pytest.mark.django_db
def test_weekly_trends_invalid_param(client, analyst_user):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-weekly"), {"weeks": "0"})
    assert response.status_code == 400



@pytest.mark.django_db
def test_recent_activity_default_limit(client, analyst_user, seed_transactions):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-activity"))
    assert response.status_code == 200
    assert len(response.data["data"]) == 5


@pytest.mark.django_db
def test_recent_activity_custom_limit(client, analyst_user, seed_transactions):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-activity"), {"limit": "2"})
    assert response.status_code == 200
    assert len(response.data["data"]) == 2


@pytest.mark.django_db
def test_recent_activity_invalid_limit(client, analyst_user):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("dashboard-activity"), {"limit": "999"})
    assert response.status_code == 400


@pytest.mark.django_db
def test_viewer_cannot_access_activity(client, viewer_user):
    authed = auth_client(client, viewer_user)
    response = authed.get(reverse("dashboard-activity"))
    assert response.status_code == 403