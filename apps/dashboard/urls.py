from django.urls import path
from apps.dashboard.views import (
    SummaryView,
    CategoryBreakdownView,
    MonthlyTrendsView,
    WeeklyTrendsView,
    RecentActivityView,
)

urlpatterns = [
    path("summary/", SummaryView.as_view(), name="dashboard-summary"),
    path("categories/", CategoryBreakdownView.as_view(), name="dashboard-categories"),
    path("trends/monthly/", MonthlyTrendsView.as_view(), name="dashboard-monthly"),
    path("trends/weekly/", WeeklyTrendsView.as_view(), name="dashboard-weekly"),
    path("activity/", RecentActivityView.as_view(), name="dashboard-activity"),
]