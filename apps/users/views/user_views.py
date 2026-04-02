from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from apps.users.models import User
from apps.users.serializers import UserSerializer, UserUpdateSerializer
from apps.users.permissions import IsAdmin


class UserListView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(
        responses={200: UserSerializer(many=True)},
        summary="List all users",
        tags=["Users"],
    )
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class UserDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    @extend_schema(
        responses={200: UserSerializer},
        summary="Retrieve a user",
        tags=["Users"],
    )
    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        summary="Update a user's role or status",
        tags=["Users"],
    )
    def patch(self, request, pk):
        user = self.get_object(pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "User updated successfully.",
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a user",
        tags=["Users"],
    )
    def delete(self, request, pk):
        user = self.get_object(pk)
        if user == request.user:
            return Response(
                {"success": False, "error": {"detail": "You cannot delete your own account."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response(
            {"success": True, "message": "User deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class MeView(APIView):
    @extend_schema(
        responses={200: UserSerializer},
        summary="Get current authenticated user",
        tags=["Users"],
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )