from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek
from apps.finance.models import Transaction
import datetime


def get_summary(user_filter=None):
    """
    Total income, total expenses, net balance, transaction count.
    """
    qs = Transaction.objects.all()

    totals = qs.aggregate(
        total_income=Sum("amount", filter=Q(type=Transaction.Type.INCOME)),
        total_expenses=Sum("amount", filter=Q(type=Transaction.Type.EXPENSE)),
        total_transactions=Count("id"),
    )

    total_income = totals["total_income"] or 0
    total_expenses = totals["total_expenses"] or 0
    net_balance = total_income - total_expenses

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(net_balance, 2),
        "total_transactions": totals["total_transactions"],
    }


def get_category_breakdown():
    """
    Per-category totals split by income and expense.
    """
    qs = (
        Transaction.objects
        .values("category", "type")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("category", "type")
    )

    breakdown = {}
    for row in qs:
        cat = row["category"]
        if cat not in breakdown:
            breakdown[cat] = {"category": cat, "income": 0, "expense": 0, "count": 0}
        breakdown[cat][row["type"]] = round(float(row["total"]), 2)
        breakdown[cat]["count"] += row["count"]

    return list(breakdown.values())


def get_monthly_trends(months=12):
    """
    Month-by-month income vs expense totals for the last N months.
    """
    since = datetime.date.today().replace(day=1) - datetime.timedelta(days=30 * (months - 1))

    qs = (
        Transaction.objects
        .filter(date__gte=since)
        .annotate(month=TruncMonth("date"))
        .values("month", "type")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("month", "type")
    )

    trends = {}
    for row in qs:
        key = row["month"].strftime("%Y-%m")
        if key not in trends:
            trends[key] = {"month": key, "income": 0, "expense": 0, "count": 0}
        trends[key][row["type"]] = round(float(row["total"]), 2)
        trends[key]["count"] += row["count"]

    return list(trends.values())


def get_weekly_trends(weeks=8):
    """
    Week-by-week income vs expense totals for the last N weeks.
    """
    since = datetime.date.today() - datetime.timedelta(weeks=weeks)

    qs = (
        Transaction.objects
        .filter(date__gte=since)
        .annotate(week=TruncWeek("date"))
        .values("week", "type")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("week", "type")
    )

    trends = {}
    for row in qs:
        key = row["week"].strftime("%Y-%m-%d")
        if key not in trends:
            trends[key] = {"week": key, "income": 0, "expense": 0, "count": 0}
        trends[key][row["type"]] = round(float(row["total"]), 2)
        trends[key]["count"] += row["count"]

    return list(trends.values())


def get_recent_transactions(limit=10):
    """
    Most recent N transactions for activity feed.
    """
    from apps.finance.serializers import TransactionSerializer
    qs = (
        Transaction.objects
        .select_related("created_by")
        .order_by("-date", "-created_at")[:limit]
    )
    return TransactionSerializer(qs, many=True).data