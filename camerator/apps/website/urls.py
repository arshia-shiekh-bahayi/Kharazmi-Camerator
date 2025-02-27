from django.urls import path

from apps.website import views

app_name = "website"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index-view"),
    path("contact/", views.ContactUsFormView.as_view(), name="contact-us-view"),
    path("about/", views.AboutView.as_view(), name="about-us-view"),
    path(
        "newsletter/form",
        views.NewsletterCreateView.as_view(),
        name="newsletter-form-view",
    ),
]
