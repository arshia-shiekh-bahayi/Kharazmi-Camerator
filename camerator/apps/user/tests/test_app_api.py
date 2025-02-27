import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import AuthRequest, User
from apps.user.tests.factories import UserFactory
from services.kavenegar import KavenegarResult
from utils.testcases import AppAPITestCase


class TestUserViewSet(AppAPITestCase):
    def test_me(self):
        url = "/api/v1/users/me/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["username"], self.customer.username)
        self.assertEqual(response["first_name"], self.customer.first_name)
        self.assertEqual(response["last_name"], self.customer.last_name)

    def test_user_can_update_his_info(self):
        previous_user_username = self.customer.username
        data = {
            "first_name": "FN",
            "last_name": "LN",
            "username": "NOT_GONNA_CHANGE",
            "national_code": "123",
        }
        url = "/api/v1/users/me/"
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, "FN")
        self.assertEqual(self.customer.last_name, "LN")
        self.assertEqual(self.customer.username, previous_user_username)
        self.assertEqual(self.customer.national_code, "123")


class TestAuthViewSet(APITestCase):
    def setUp(self):
        self.customer: User = UserFactory()
        self.client = APIClient()

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_get_mobile(self, kavenegar_mock: MagicMock):
        kavenegar_mock.return_value = KavenegarResult(
            response_code=200, response_message=""
        )
        url = "/api/v1/auth/mobile/"

        invalid_mobile_numbers = [
            "091",  # Less than 11 digits
            "091234567890",  # More than 11 digits
            "",  # Empty Mobile
            "09123c56789",  # 11 digits but contains char
            "19123456789",  # 11 digits but doesn't start with 09
        ]

        for mobile in invalid_mobile_numbers:
            response = self.client.post(url, data={"mobile": mobile}, format="json")
            self.assertEqual(response.status_code, 400)
            expected_error_code = "invalid_input" if mobile else "blank"
            response = response.json()
            self.assertEqual(response["type"], "validation_error")
            self.assertEqual(response["code"], expected_error_code)
            self.assertEqual(response["attr"], "mobile")

        unregistered_mobile = "09123456789"
        response = self.client.post(
            url, data={"mobile": unregistered_mobile}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("id", response)
        self.assertIn("user_is_registered", response)
        self.assertEqual(response["user_is_registered"], False)

        registered_mobile = self.customer.username
        response = self.client.post(
            url, data={"mobile": registered_mobile}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("id", response)
        self.assertIn("user_is_registered", response)
        self.assertEqual(response["user_is_registered"], True)

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_complete_auth_for_already_registered_users(
        self, kavenegar_mock: MagicMock
    ):
        kavenegar_mock.return_value = KavenegarResult(
            response_code=200, response_message=""
        )
        registered_mobile = self.customer.username
        mobile_url = "/api/v1/auth/mobile/"
        response = self.client.post(
            mobile_url, data={"mobile": registered_mobile}, format="json"
        )
        auth_id = response.json()["id"]
        otp_code = AuthRequest.objects.get(id=auth_id).otp_code

        url = f"/api/v1/auth/{auth_id}/code/"
        response = self.client.post(url, data={"otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("id", response)
        self.assertIn("refresh_token", response)
        self.assertIn("access_token", response)
        self.assertIn("expires_at", response)
        self.assertIn("user_is_registered", response)
        self.assertEqual(response["user_is_registered"], True)

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_complete_auth_for_already_registered_users_with_wrong_data(
        self, kavenegar_mock: MagicMock
    ):
        kavenegar_mock.return_value = KavenegarResult(
            response_code=200, response_message=""
        )
        registered_mobile = self.customer.username
        mobile_url = "/api/v1/auth/mobile/"
        response = self.client.post(
            mobile_url, data={"mobile": registered_mobile}, format="json"
        )
        auth_id = response.json()["id"]
        auth_request = AuthRequest.objects.get(id=auth_id)
        otp_code = auth_request.otp_code

        # wrong auth_id type
        url = "/api/v1/auth/WRONG_AUTH_ID/code/"
        response = self.client.post(url, data={"otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, 404)

        # wrong auth_id
        url = f"/api/v1/auth/{uuid.uuid4()}/code/"
        response = self.client.post(url, data={"otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, 404)

        # wrong otp codes
        url = f"/api/v1/auth/{auth_id}/code/"
        wrong_otp_codes = [
            "STRING_AS_OTP_CODE",
            "123",  # less than 5 digit otp code
            "123456",  # more than 5 digit otp code
            "12345",  # wrong otp code
        ]
        for code in wrong_otp_codes:
            response = self.client.post(url, data={"otp_code": code}, format="json")
            self.assertEqual(response.status_code, 400)
            response = response.json()
            self.assertEqual(response["type"], "validation_error")
            self.assertEqual(response["attr"], "otp_code")

        # Expired OTP Code
        faked_now = timezone.now() + timedelta(minutes=10)
        with patch("django.utils.timezone.now", return_value=faked_now):
            response = self.client.post(url, data={"otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")
        self.assertEqual(response["attr"], "otp_code")

        # Closed AuthRequest
        auth_request.close_request()
        response = self.client.post(url, data={"otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        print(response)
        self.assertEqual(response["type"], "validation_error")

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_complete_auth_for_unregistered_users(self, kavenegar_mock: MagicMock):
        kavenegar_mock.return_value = KavenegarResult(
            response_code=200, response_message=""
        )
        unregistered_mobile = "09123456789"
        mobile_url = "/api/v1/auth/mobile/"
        response = self.client.post(
            mobile_url, data={"mobile": unregistered_mobile}, format="json"
        )
        auth_id = response.json()["id"]
        otp_code = AuthRequest.objects.get(id=auth_id).otp_code

        # Send request without first_name, last_name and national_code
        data = {"otp_code": otp_code}
        url = f"/api/v1/auth/{auth_id}/code/"
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")
        self.assertEqual(response["attr"], "first_name")

        first_name = "first_name"
        last_name = "last_name"
        national_code = "1234567890"

        data = {
            "otp_code": otp_code,
            "first_name": first_name,
            "national_code": national_code,
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        print(response)
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")
        self.assertEqual(response["attr"], "last_name")

        data = {"otp_code": otp_code, "first_name": first_name, "last_name": last_name}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")
        self.assertEqual(response["attr"], "national_code")

        # Wrong national code
        data = {
            "otp_code": otp_code,
            "first_name": first_name,
            "last_name": last_name,
            "national_code": "CHAR",
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")
        self.assertEqual(response["attr"], "national_code")

        # Wrong national code
        data = {
            "otp_code": otp_code,
            "first_name": first_name,
            "last_name": last_name,
            "national_code": "123",
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")
        self.assertEqual(response["attr"], "national_code")

        # Send otp code with first name, last name and national_code
        users_count = User.objects.count()
        data = {
            "otp_code": otp_code,
            "first_name": first_name,
            "last_name": last_name,
            "national_code": national_code,
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("id", response)
        self.assertIn("refresh_token", response)
        self.assertIn("access_token", response)
        self.assertIn("expires_at", response)
        self.assertIn("user_is_registered", response)
        self.assertEqual(User.objects.count(), users_count + 1)

    @patch("services.kavenegar.Kavenegar.send_request")
    def test_resend_code(self, kavenegar_mock: MagicMock):
        kavenegar_mock.return_value = KavenegarResult(
            response_code=200, response_message=""
        )
        registered_mobile = self.customer.username
        mobile_url = "/api/v1/auth/mobile/"
        response = self.client.post(
            mobile_url, data={"mobile": registered_mobile}, format="json"
        )
        auth_id = response.json()["id"]
        auth_request: AuthRequest = AuthRequest.objects.get(id=auth_id)
        old_otp_code = auth_request.otp_code

        url = f"/api/v1/auth/{auth_id}/resend-code/"
        # Resend code before expiry of the old code
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response["type"], "validation_error")
        self.assertEqual(response["code"], "invalid_input")

        # Resend code one minute after expiry of the old code
        faked_now = timezone.now() + timedelta(minutes=6)
        with patch("django.utils.timezone.now", return_value=faked_now):
            response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        auth_request.refresh_from_db()
        self.assertEqual(auth_request.expire_datetime, faked_now + timedelta(minutes=5))
        self.assertNotEqual(old_otp_code, auth_request.otp_code)

    def test_refresh_token(self):
        token = RefreshToken().for_user(self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

        url = "/api/v1/auth/refresh-token/"
        response = self.client.post(
            url, data={"refresh_token": str(token)}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("access_token", response)
        self.assertIn("expires_at", response)
