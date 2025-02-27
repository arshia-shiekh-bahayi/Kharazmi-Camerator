from django.urls import path

from apps.service import views

app_name = "service"

urlpatterns = [path("list/", views.ServiceListView.as_view(), name="list-view")]
