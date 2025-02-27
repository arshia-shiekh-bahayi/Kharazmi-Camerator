import uuid

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ErrorDetail, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import AuthRequest, User
from services.sms_service import SMSServiceException


class GetMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthRequest
        fields = ["id", "mobile", "user_is_registered"]
        read_only_fields = ["id", "user_is_registered"]
        extra_kwargs = {"mobile": {"write_only": True}}

    @staticmethod
    def create(validated_data: dict[str, str]) -> AuthRequest:
        auth_request: AuthRequest = AuthRequest(mobile=validated_data["mobile"])
        user: User | None = auth_request.get_user_or_none()
        if user:
            auth_request.user_is_registered = True
        auth_request.save()
        try:
            auth_request.send_otp_code()
        except SMSServiceException as ex:
            raise APIException from ex
        return auth_request


class LoginSignupSerializer(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = AuthRequest
        fields = [
            "id",
            "otp_code",
            "first_name",
            "last_name",
            "national_code",
            "user_is_registered",
            "refresh_token",
            "access_token",
            "expires_at",
        ]
        extra_kwargs = {
            "otp_code": {"required": True, "write_only": True},
            "first_name": {"write_only": True},
            "last_name": {"write_only": True},
            "national_code": {"write_only": True},
            "user_is_registered": {"read_only": True},
        }

    def validate(self, validated_data: dict[str, str]) -> dict:
        auth_request = self.context["auth_request"]

        if not auth_request.user_is_registered:
            first_name = validated_data.get("first_name")
            last_name = validated_data.get("last_name")
            national_code = validated_data.get("national_code")
            if not first_name:
                raise ValidationError({"first_name": _("First name is required.")})
            if not last_name:
                raise ValidationError({"last_name": _("Last name is required.")})
            if not national_code:
                raise ValidationError(
                    {"national_code": _("National code is required.")}
                )
            if not national_code.isdigit():
                raise ValidationError(
                    {"national_code": _("National code should be only digits.")}
                )
            if len(national_code) != 10:
                raise ValidationError(
                    {"national_code": _("National code should be 10 digits.")}
                )

        if auth_request.is_closed():
            raise ValidationError(
                ErrorDetail(_("The refresh token is closed."), code="closed")
            )

        if auth_request.is_expired():
            auth_request.close_request()
            raise ValidationError({"otp_code": _("The OTP code is expired.")})

        if auth_request.otp_code != validated_data["otp_code"]:
            raise ValidationError(
                {
                    "otp_code": _(
                        f"The OTP code for mobile {auth_request.mobile} is invalid."
                    )
                }
            )
        return validated_data

    def create(self, validated_data) -> AuthRequest:
        auth_request = self.context["auth_request"]

        if not auth_request.user_is_registered:
            auth_request.first_name = validated_data["first_name"]
            auth_request.last_name = validated_data["last_name"]
            auth_request.national_code = validated_data["national_code"]
            auth_request.create_new_user()
        auth_request.close_request()

        _user: User = get_object_or_404(User, username=auth_request.mobile)

        token: RefreshToken = RefreshToken.for_user(_user)
        auth_request.access_token = str(token.access_token)
        auth_request.refresh_token = str(token)
        auth_request.expires_at = token.access_token["exp"]
        return auth_request

    @staticmethod
    def get_refresh_token(obj: AuthRequest) -> str:
        return getattr(obj, "refresh_token", "")

    @staticmethod
    def get_access_token(obj: AuthRequest) -> str:
        return getattr(obj, "access_token", "")

    @staticmethod
    def get_expires_at(obj: AuthRequest) -> str:
        return getattr(obj, "expires_at", "")


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    expires_at = serializers.CharField(read_only=True)

    @staticmethod
    def validate(attrs: dict) -> dict:
        refresh = RefreshToken(attrs["refresh_token"])
        data = {"access_token": str(refresh.access_token)}
        if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
            if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            data["refresh_token"] = str(refresh)
        data["expires_at"] = refresh.access_token.get("exp")
        return data


class AuthRequestViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        method="POST",
        request_body=GetMobileSerializer(),
        responses={200: GetMobileSerializer()},
    )
    @action(detail=False, methods=["POST"])
    def mobile(self, request: Request) -> Response:
        serializer = GetMobileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(
        method="POST",
        request_body=LoginSignupSerializer(),
        responses={200: LoginSignupSerializer()},
    )
    @action(detail=True, methods=["POST"])
    def code(self, request: Request, pk: uuid.UUID) -> Response:
        try:
            auth_request: AuthRequest = AuthRequest.objects.get(id=pk)
        except (DjangoValidationError, AuthRequest.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
        auth_request.disable_previous_codes()
        serializer = LoginSignupSerializer(
            data=request.data, context={"auth_request": auth_request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(method="POST", responses={200: ""})
    @action(detail=True, methods=["POST"], url_path="resend-code")
    def resend_code(self, request: Request, pk: uuid.UUID) -> Response:
        auth_request: AuthRequest = get_object_or_404(AuthRequest, id=pk)
        if auth_request.is_closed():
            raise ValidationError(_("The request is closed. Try again."))
        if not auth_request.is_expired():
            raise ValidationError(_("The previous OTP code has not expired yet."))
        try:
            auth_request.resend_otp_code()
        except SMSServiceException as ex:
            raise APIException from ex
        return Response()

    @swagger_auto_schema(
        method="POST",
        request_body=TokenRefreshSerializer(),
        responses={200: TokenRefreshSerializer()},
    )
    @action(detail=False, methods=["POST"], url_path="refresh-token")
    def refresh_token(self, request: Request) -> Response:
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
