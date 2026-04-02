from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.users.permissions import IsAnalystOrAbove, IsAnyAuthenticatedUser
from apps.dashboard import services


class SummaryView(APIView):
    permission_classes = [IsAnyAuthenticatedUser]

    @extend_schema(
        summary="Get financial summary",
        description="Returns total income, total expenses, net balance and transaction count.",
        responses={200: None},
        tags=["Dashboard"],
    )
    def get(self, request):
        data = services.get_summary()
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )


class CategoryBreakdownView(APIView):
    permission_classes = [IsAnalystOrAbove]

    @extend_schema(
        summary="Get category breakdown",
        description="Returns income and expense totals grouped by category.",
        responses={200: None},
        tags=["Dashboard"],
    )
    def get(self, request):
        data = services.get_category_breakdown()
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )


class MonthlyTrendsView(APIView):
    permission_classes = [IsAnalystOrAbove]

    @extend_schema(
        summary="Get monthly trends",
        description="Returns month-by-month income vs expense totals.",
        parameters=[
            OpenApiParameter(
                "months",
                OpenApiTypes.INT,
                description="Number of months to look back (default: 12, max: 24)",
            )
        ],
        responses={200: None},
        tags=["Dashboard"],
    )
    def get(self, request):
        try:
            months = int(request.GET.get("months", 12))
            if not (1 <= months <= 24):
                raise ValueError
        except ValueError:
            return Response(
                {"success": False, "error": {"detail": "months must be an integer between 1 and 24."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_monthly_trends(months=months)
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )


class WeeklyTrendsView(APIView):
    permission_classes = [IsAnalystOrAbove]

    @extend_schema(
        summary="Get weekly trends",
        description="Returns week-by-week income vs expense totals.",
        parameters=[
            OpenApiParameter(
                "weeks",
                OpenApiTypes.INT,
                description="Number of weeks to look back (default: 8, max: 52)",
            )
        ],
        responses={200: None},
        tags=["Dashboard"],
    )
    def get(self, request):
        try:
            weeks = int(request.GET.get("weeks", 8))
            if not (1 <= weeks <= 52):
                raise ValueError
        except ValueError:
            return Response(
                {"success": False, "error": {"detail": "weeks must be an integer between 1 and 52."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_weekly_trends(weeks=weeks)
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )


class RecentActivityView(APIView):
    permission_classes = [IsAnalystOrAbove]

    @extend_schema(
        summary="Get recent transactions",
        description="Returns the most recent transactions for the activity feed.",
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Number of transactions to return (default: 10, max: 50)",
            )
        ],
        responses={200: None},
        tags=["Dashboard"],
    )
    def get(self, request):
        try:
            limit = int(request.GET.get("limit", 10))
            if not (1 <= limit <= 50):
                raise ValueError
        except ValueError:
            return Response(
                {"success": False, "error": {"detail": "limit must be an integer between 1 and 50."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = services.get_recent_transactions(limit=limit)
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )