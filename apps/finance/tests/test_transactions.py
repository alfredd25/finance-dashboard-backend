import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.finance.models import Transaction
import datetime


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
def transaction(db, admin_user):
    return Transaction.objects.create(
        amount="500.00",
        type="income",
        category="salary",
        date=datetime.date.today(),
        notes="Test transaction",
        created_by=admin_user,
    )


def auth_client(client, user):
    response = client.post(reverse("auth-login"), {
        "email": user.email,
        "password": "StrongPass123!",
    }, format="json")
    token = response.data["data"]["tokens"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# --- List ---

@pytest.mark.django_db
def test_analyst_can_list_transactions(client, analyst_user, transaction):
    authed = auth_client(client, analyst_user)
    response = authed.get(reverse("transaction-list"))
    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_viewer_cannot_list_transactions(client, viewer_user):
    authed = auth_client(client, viewer_user)
    response = authed.get(reverse("transaction-list"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_unauthenticated_cannot_list_transactions(client):
    response = client.get(reverse("transaction-list"))
    assert response.status_code == 401


# --- Pagination ---

@pytest.mark.django_db
def test_pagination_structure(client, admin_user):
    for i in range(25):
        Transaction.objects.create(
            amount="100.00",
            type="income",
            category="other",
            date=datetime.date.today(),
            created_by=admin_user,
        )
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"))
    assert response.status_code == 200
    assert response.data["count"] == 25
    assert response.data["total_pages"] == 2
    assert response.data["current_page"] == 1
    assert len(response.data["data"]) == 20


@pytest.mark.django_db
def test_pagination_page_size(client, admin_user):
    for i in range(10):
        Transaction.objects.create(
            amount="100.00",
            type="income",
            category="other",
            date=datetime.date.today(),
            created_by=admin_user,
        )
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"), {"page_size": "5"})
    assert response.status_code == 200
    assert len(response.data["data"]) == 5
    assert response.data["total_pages"] == 2


# --- Search ---

@pytest.mark.django_db
def test_search_by_notes(client, admin_user):
    Transaction.objects.create(
        amount="100.00", type="income", category="other",
        date=datetime.date.today(), notes="bonus payment", created_by=admin_user,
    )
    Transaction.objects.create(
        amount="200.00", type="expense", category="rent",
        date=datetime.date.today(), notes="monthly rent", created_by=admin_user,
    )
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"), {"search": "bonus"})
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["data"][0]["notes"] == "bonus payment"


@pytest.mark.django_db
def test_search_by_category(client, admin_user):
    Transaction.objects.create(
        amount="500.00", type="income", category="freelance",
        date=datetime.date.today(), created_by=admin_user,
    )
    Transaction.objects.create(
        amount="200.00", type="expense", category="groceries",
        date=datetime.date.today(), created_by=admin_user,
    )
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"), {"search": "freelance"})
    assert response.status_code == 200
    assert response.data["count"] == 1


# --- Filtering ---

@pytest.mark.django_db
def test_filter_by_type(client, admin_user, transaction):
    Transaction.objects.create(
        amount="200.00", type="expense", category="rent",
        date=datetime.date.today(), created_by=admin_user,
    )
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"), {"type": "income"})
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["data"][0]["type"] == "income"


@pytest.mark.django_db
def test_filter_by_category(client, admin_user, transaction):
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"), {"category": "salary"})
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_filter_by_date_range(client, admin_user):
    Transaction.objects.create(
        amount="100.00", type="income", category="other",
        date=datetime.date(2024, 1, 15), created_by=admin_user,
    )
    Transaction.objects.create(
        amount="200.00", type="expense", category="rent",
        date=datetime.date(2024, 6, 15), created_by=admin_user,
    )
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"), {
        "date_from": "2024-06-01",
        "date_to": "2024-12-31",
    })
    assert response.status_code == 200
    assert response.data["count"] == 1


# --- Create ---

@pytest.mark.django_db
def test_admin_can_create_transaction(client, admin_user):
    authed = auth_client(client, admin_user)
    response = authed.post(reverse("transaction-list"), {
        "amount": "1500.00",
        "type": "income",
        "category": "salary",
        "date": str(datetime.date.today()),
        "notes": "Monthly salary",
    }, format="json")
    assert response.status_code == 201
    assert response.data["success"] is True
    assert Transaction.objects.count() == 1


@pytest.mark.django_db
def test_analyst_cannot_create_transaction(client, analyst_user):
    authed = auth_client(client, analyst_user)
    response = authed.post(reverse("transaction-list"), {
        "amount": "1500.00",
        "type": "income",
        "category": "salary",
        "date": str(datetime.date.today()),
    }, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_transaction_invalid_amount(client, admin_user):
    authed = auth_client(client, admin_user)
    response = authed.post(reverse("transaction-list"), {
        "amount": "-100.00",
        "type": "income",
        "category": "salary",
        "date": str(datetime.date.today()),
    }, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_transaction_missing_fields(client, admin_user):
    authed = auth_client(client, admin_user)
    response = authed.post(reverse("transaction-list"), {
        "amount": "100.00",
    }, format="json")
    assert response.status_code == 400


# --- Retrieve ---

@pytest.mark.django_db
def test_analyst_can_retrieve_transaction(client, analyst_user, transaction):
    authed = auth_client(client, analyst_user)
    response = authed.get(
        reverse("transaction-detail", kwargs={"pk": transaction.id})
    )
    assert response.status_code == 200
    assert str(response.data["data"]["id"]) == str(transaction.id)


@pytest.mark.django_db
def test_viewer_cannot_retrieve_transaction(client, viewer_user, transaction):
    authed = auth_client(client, viewer_user)
    response = authed.get(
        reverse("transaction-detail", kwargs={"pk": transaction.id})
    )
    assert response.status_code == 403


# --- Update ---

@pytest.mark.django_db
def test_admin_can_update_transaction(client, admin_user, transaction):
    authed = auth_client(client, admin_user)
    response = authed.patch(
        reverse("transaction-detail", kwargs={"pk": transaction.id}),
        {"amount": "999.99", "notes": "Updated"},
        format="json",
    )
    assert response.status_code == 200
    transaction.refresh_from_db()
    assert float(transaction.amount) == 999.99


@pytest.mark.django_db
def test_analyst_cannot_update_transaction(client, analyst_user, transaction):
    authed = auth_client(client, analyst_user)
    response = authed.patch(
        reverse("transaction-detail", kwargs={"pk": transaction.id}),
        {"amount": "999.99"},
        format="json",
    )
    assert response.status_code == 403


# --- Soft Delete ---

@pytest.mark.django_db
def test_admin_can_delete_transaction(client, admin_user, transaction):
    authed = auth_client(client, admin_user)
    response = authed.delete(
        reverse("transaction-detail", kwargs={"pk": transaction.id})
    )
    assert response.status_code == 200
    assert Transaction.objects.count() == 0
    assert Transaction.all_objects.count() == 1


@pytest.mark.django_db
def test_soft_deleted_transaction_not_in_list(client, admin_user, transaction):
    transaction.soft_delete()
    authed = auth_client(client, admin_user)
    response = authed.get(reverse("transaction-list"))
    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_analyst_cannot_delete_transaction(client, analyst_user, transaction):
    authed = auth_client(client, analyst_user)
    response = authed.delete(
        reverse("transaction-detail", kwargs={"pk": transaction.id})
    )
    assert response.status_code == 403