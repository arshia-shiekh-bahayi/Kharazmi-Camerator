from dataclasses import dataclass
from enum import Enum

import requests

from .exceptions import KavenegarRequestException, MobileNumberException
from .validators import validate_phone_number


class KavenegarTemplate(Enum):
    OTP_CODE = "otp_code"


class MobileNumber(str):
    """Mobile number is a string of 11 digits."""

    def __init__(self, value: str):
        if not validate_phone_number(value):
            raise MobileNumberException()


@dataclass
class KavenegarResult:
    response_code: int
    response_message: str


class Kavenegar:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    @staticmethod
    def _raw_send(template, receptor, tokens, api_key):
        url = f"https://api.kavenegar.com/v1/{api_key}/verify/lookup.json"
        params = {"receptor": receptor, "template": template, **tokens}
        return requests.post(url, params=params)

    def send_request(
        self, mobile_number: MobileNumber, template: KavenegarTemplate, **kwargs: str
    ) -> KavenegarResult:
        args = ",".join(f"{k}:{v}" for k, v in kwargs.items())
        print("--------------------------BEGIN KAVENEGAR SMS--------------------------")
        print(f"\t{mobile_number = }")
        print(f"\t{template.name = }")
        print(f"\t{args = }")
        print("--------------------------END KAVENEGAR SMS--------------------------")

        tokens = {}
        for index, value in enumerate(kwargs.values()):
            prefix = "" if index == 0 else index + 1
            tokens[f"token{prefix}"] = value
        response = self._raw_send(
            template.value, mobile_number, api_key=self.api_key, tokens=tokens
        )
        if response.status_code != 200:
            raise KavenegarRequestException()
        response = response.json()
        ret = response["return"]
        return KavenegarResult(
            response_code=ret["status"], response_message=ret["message"]
        )
