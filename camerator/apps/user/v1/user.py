from typing import cast

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "national_code"]
        read_only_fields = [
            "username",
        ]
        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class UserViewSet(GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        user = cast(User, self.request.user)
        assert isinstance(user.id, int)
        return self.queryset.filter(id=user.id)

    @action(detail=False, methods=["GET", "PATCH"])
    def me(self, request: Request):
        if request.method and request.method.lower() == "patch":
            return self.me_update(request)
        return self.me_retrieve(request)

    @staticmethod
    def me_retrieve(request: Request) -> Response:
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @staticmethod
    def me_update(request: Request) -> Response:
        serializer = UserSerializer(
            request.user, context={"request": request}, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)
