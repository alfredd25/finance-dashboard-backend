from django.urls import path
from apps.finance.views import TransactionListView, TransactionDetailView

urlpatterns = [
    path("", TransactionListView.as_view(), name="transaction-list"),
    path("<uuid:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
]