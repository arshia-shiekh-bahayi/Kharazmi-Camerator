from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone

from apps.user.models import AuthRequest, User
from apps.user.tests.factories import AuthRequestFactory, UserFactory
from services.kavenegar import KavenegarTemplate


class UserModelTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_str_method(self):
        self.assertEqual(
            str(self.user),
            f"{self.user.username} ({self.user.first_name} {self.user.last_name})",
        )

    def test_only_mobile_number_is_required(self):
        self.assertEqual(User.objects.count(), 1)
        valid_mobile = "09123456789"
        User.objects.create(username=valid_mobile)
        self.assertEqual(User.objects.count(), 2)


class AuthRequestTestCase(TestCase):
    def setUp(self):
        self.user: User = UserFactory()
        self.auth: AuthRequest = AuthRequestFactory()

    def test_is_expired(self):
        now = timezone.now()
        with patch("django.utils.timezone.now", return_value=now):
            auth: AuthRequest = AuthRequest.objects.create(mobile="09123456789")
        self.assertEqual(auth.expire_datetime, now + timedelta(minutes=5))
        self.assertFalse(auth.is_expired())
        with patch(
            "django.utils.timezone.now", return_value=now + timedelta(minutes=7)
        ):
            self.assertTrue(auth.is_expired())

    def test_is_closed(self):
        auth: AuthRequest = AuthRequest.objects.create(mobile="09123456789")
        self.assertEqual(auth.request_status, AuthRequest.RequestStatuses.PENDING)
        self.assertFalse(auth.is_closed())
        auth.request_status = AuthRequest.RequestStatuses.COMPLETED
        auth.save()
        self.assertEqual(auth.request_status, AuthRequest.RequestStatuses.COMPLETED)
        self.assertTrue(auth.is_closed())

    def test_close_request(self):
        auth: AuthRequest = AuthRequest.objects.create(mobile="09123456789")
        self.assertEqual(auth.request_status, AuthRequest.RequestStatuses.PENDING)
        auth.close_request()
        self.assertEqual(auth.request_status, AuthRequest.RequestStatuses.COMPLETED)

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_send_otp_code(self, mock_sms_service: MagicMock):
        auth: AuthRequest = AuthRequest.objects.create(mobile="09123456789")
        self.assertIsNone(auth.otp_code)
        auth.send_otp_code()
        self.assertIsNotNone(auth.otp_code)
        mock_sms_service.assert_called_once_with(
            auth.mobile, KavenegarTemplate.OTP_CODE, otp_code=auth.otp_code
        )

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_resend_otp_code(self, mock_sms_service: MagicMock):
        now = timezone.now()
        with patch("django.utils.timezone.now", return_value=now):
            auth: AuthRequest = AuthRequest.objects.create(mobile="09123456789")
        self.assertEqual(auth.expire_datetime, now + timedelta(minutes=5))
        self.assertIsNone(auth.otp_code)

        now = timezone.now()
        with patch("django.utils.timezone.now", return_value=now):
            auth.resend_otp_code()
        auth.refresh_from_db()
        self.assertEqual(auth.expire_datetime, now + timedelta(minutes=5))
        self.assertIsNotNone(auth.otp_code)
        mock_sms_service.assert_called_once_with(
            auth.mobile, KavenegarTemplate.OTP_CODE, otp_code=auth.otp_code
        )

    def test_str_method(self):
        expected_str = f"{self.auth.mobile} - {self.auth.created_at}"
        self.assertEqual(str(self.auth), expected_str)
