from faker import Faker
from rest_framework.test import APIClient, APITestCase, APITransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User
from apps.user.tests.factories import UserFactory


class AppAPITestCase(APITestCase):
    def setUp(self):
        self.faker = Faker()
        self.customer: User = UserFactory()
        token = RefreshToken().for_user(self.customer)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")


class DashboardAPITestCase(APITransactionTestCase):
    def setUp(self):
        self.faker = Faker()
        self.admin: User = UserFactory(is_superuser=True)
        token = RefreshToken().for_user(self.admin)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
