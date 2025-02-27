from collections.abc import Sequence
from random import randint
from typing import Any

from factory import Faker, LazyFunction, post_generation
from factory.django import DjangoModelFactory

from apps.user.models import AuthRequest, User


class UserFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    username = LazyFunction(lambda: make_phone_number())

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = User
        django_get_or_create = ["username"]


class AuthRequestFactory(DjangoModelFactory):
    mobile = LazyFunction(lambda: make_phone_number())

    class Meta:
        model = AuthRequest
        django_get_or_create = ["mobile"]


def make_phone_number() -> str:
    prefix = "09"
    return prefix + str(randint(10_000_0000, 99_999_9999))
