from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from apps.finance.models import Transaction
from apps.finance.serializers import TransactionSerializer, TransactionCreateUpdateSerializer
from apps.finance.filters import TransactionFilter
from apps.users.permissions import IsAdmin, IsAnalystOrAbove


class TransactionListView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsAnalystOrAbove()]

    @extend_schema(
        summary="List all transactions",
        description="Returns all transactions. Supports filtering by type, category, date range, and amount range.",
        parameters=[
            OpenApiParameter("type", OpenApiTypes.STR, description="Filter by type: income or expense"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filter by category"),
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Filter from date (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Filter to date (YYYY-MM-DD)"),
            OpenApiParameter("amount_min", OpenApiTypes.FLOAT, description="Minimum amount"),
            OpenApiParameter("amount_max", OpenApiTypes.FLOAT, description="Maximum amount"),
            OpenApiParameter("ordering", OpenApiTypes.STR, description="Order by: date, amount, created_at (prefix - for descending)"),
        ],
        responses={200: TransactionSerializer(many=True)},
        tags=["Transactions"],
    )
    def get(self, request):
        queryset = Transaction.objects.select_related("created_by").all()

        filterset = TransactionFilter(request.GET, queryset=queryset)
        if not filterset.is_valid():
            return Response(
                {"success": False, "error": {"detail": filterset.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = filterset.qs

        ordering = request.GET.get("ordering", "-date")
        allowed_ordering = ["date", "-date", "amount", "-amount", "created_at", "-created_at"]
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Create a transaction",
        request=TransactionCreateUpdateSerializer,
        responses={201: TransactionSerializer},
        tags=["Transactions"],
    )
    @method_decorator(ratelimit(key="user", rate="60/m", method="POST", block=True))
    def post(self, request):
        serializer = TransactionCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save(created_by=request.user)
        return Response(
            {
                "success": True,
                "message": "Transaction created successfully.",
                "data": TransactionSerializer(transaction).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TransactionDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAdmin()]
        return [IsAnalystOrAbove()]

    def get_object(self, pk):
        return get_object_or_404(
            Transaction.objects.select_related("created_by"), pk=pk
        )

    @extend_schema(
        summary="Retrieve a transaction",
        responses={200: TransactionSerializer},
        tags=["Transactions"],
    )
    def get(self, request, pk):
        transaction = self.get_object(pk)
        serializer = TransactionSerializer(transaction)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update a transaction",
        request=TransactionCreateUpdateSerializer,
        responses={200: TransactionSerializer},
        tags=["Transactions"],
    )
    def patch(self, request, pk):
        transaction = self.get_object(pk)
        serializer = TransactionCreateUpdateSerializer(
            transaction, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Transaction updated successfully.",
                "data": TransactionSerializer(transaction).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a transaction",
        tags=["Transactions"],
    )
    def delete(self, request, pk):
        transaction = self.get_object(pk)
        transaction.delete()
        return Response(
            {"success": True, "message": "Transaction deleted successfully."},
            status=status.HTTP_200_OK,
        )