import unittest
from unittest.mock import MagicMock, patch

from services.kavenegar import KavenegarResult, KavenegarTemplate
from services.kavenegar.exceptions import MobileNumberException
from services.sms_service import OTPCodeException, SMSService, SMSServiceResult


class SMSServiceTestCase(unittest.TestCase):
    @patch("services.kavenegar.Kavenegar.send_request")
    def test_send_sms_valid_mobile_number(self, kavenegar_mock: MagicMock):
        kavenegar_mock.return_value = KavenegarResult(
            response_code=200, response_message=""
        )
        mobile = "09123456789"
        otp_code = "23054"
        result = SMSService.send_otp_code(mobile, otp_code)
        self.assertIsInstance(result, SMSServiceResult)
        self.assertTrue(hasattr(result, "mobile_number"))
        self.assertTrue(hasattr(result, "template"))
        self.assertTrue(hasattr(result, "response_code"))
        self.assertTrue(hasattr(result, "response_message"))
        self.assertTrue(hasattr(result, "kwargs"))
        self.assertEqual(result.mobile_number, mobile)
        self.assertEqual(result.template.value, KavenegarTemplate.OTP_CODE.value)
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.response_message, "")
        kwargs = result.kwargs
        self.assertIn("otp_code", kwargs)
        self.assertEqual(kwargs["otp_code"], otp_code)

    def test_send_sms_with_invalid_mobile_number(self):
        mobile = "WRONG_MOBILE_NUMBER"
        otp_code = "23054"
        with self.assertRaises(MobileNumberException):
            SMSService.send_otp_code(mobile, otp_code)

    def test_send_sms_with_invalid_otp_code(self):
        mobile = "09123456789"
        otp_code = "WRONG_OTP"
        with self.assertRaises(OTPCodeException):
            SMSService.send_otp_code(mobile, otp_code)


if __name__ == "__main__":
    unittest.main()
