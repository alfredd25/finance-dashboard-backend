from django.urls import path
from apps.users.views.user_views import UserListView, UserDetailView, MeView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("me/", MeView.as_view(), name="user-me"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
]