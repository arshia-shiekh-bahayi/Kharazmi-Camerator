from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.user.v1.auth_request import AuthRequestViewSet
from apps.user.v1.user import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("v1/users", UserViewSet)
router.register("v1/auth", AuthRequestViewSet, basename="auth")

app_name = "api"

urlpatterns = router.urls
