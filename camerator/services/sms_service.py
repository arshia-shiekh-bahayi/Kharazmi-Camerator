import random
from dataclasses import dataclass
from typing import Optional

from django.conf import settings

from services.kavenegar import Kavenegar, KavenegarRequestException, KavenegarResult, KavenegarTemplate, MobileNumber


class OTPCodeException(Exception):
    def __init__(self, message: str = "OTP code is not valid"):
        super().__init__(message)


class SMSServiceException(Exception):
    def __init__(self, message: str = "SMS Service is not reachable"):
        super().__init__(message)


class OTPCode(str):
    """OTP Code is a string of 5 digits."""

    def __init__(self, value: str):
        if len(value) != 5:
            raise OTPCodeException()

    @classmethod
    def generate(cls):
        return cls(str(random.randint(10000, 99999)))


@dataclass
class SMSServiceResult:
    mobile_number: MobileNumber
    template: KavenegarTemplate
    response_code: int
    response_message: str
    kwargs: dict[str, str]


TOTPCode = Optional[OTPCode | str]


class SMSService:
    @classmethod
    def send_otp_code(
        cls, mobile_number: MobileNumber | str, otp_code: TOTPCode = None
    ) -> SMSServiceResult:
        """
        Send the OTP Code to the mobile number using kavenegar API and return the result along with mobile_number itself
        and the otp_code. If no otp_code is provided, we generate a random otp_code.
        """
        _mobile_number: MobileNumber
        _mobile_number = (
            MobileNumber(mobile_number)
            if not isinstance(mobile_number, MobileNumber)
            else mobile_number
        )

        _otp_code: OTPCode
        _otp_code = (
            OTPCode(otp_code or OTPCode.generate())
            if not isinstance(otp_code, OTPCode)
            else otp_code
        )

        kavenegar_api = settings.KAVENEGAR_API_KEY
        debug_setting = settings.DEBUG

        kavenegar = Kavenegar(kavenegar_api)
        template = KavenegarTemplate.OTP_CODE
        try:
            result: KavenegarResult = kavenegar.send_request(
                _mobile_number, template, otp_code=_otp_code
            )
        except KavenegarRequestException as ex:
            if debug_setting:
                return SMSServiceResult(
                    mobile_number=_mobile_number,
                    template=template,
                    response_code=200,
                    response_message="",
                    kwargs={"otp_code": _otp_code},
                )
            raise SMSServiceException from ex
        return SMSServiceResult(
            mobile_number=_mobile_number,
            template=template,
            response_code=result.response_code,
            response_message=result.response_message,
            kwargs={"otp_code": _otp_code},
        )
