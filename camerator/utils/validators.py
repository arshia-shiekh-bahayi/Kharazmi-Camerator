from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class MobileValidator(validators.RegexValidator):
    regex = r"^09\d{9}$"
    message = "شماره موبایل باید به فرمت 09123456789 وارد شود"
    flags = 0
