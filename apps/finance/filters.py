import django_filters
from apps.finance.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    type = django_filters.ChoiceFilter(choices=Transaction.Type.choices)
    category = django_filters.ChoiceFilter(choices=Transaction.Category.choices)
    amount_min = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_max = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ["type", "category", "date_from", "date_to", "amount_min", "amount_max"]