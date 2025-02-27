import re


def validate_phone_number(number: str) -> bool:
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, number))
