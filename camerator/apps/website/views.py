from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.views.generic.edit import FormView

from apps.blog.models import Post
from apps.website.models import Newsletter

from .forms import ContactForm, NewsletterForm


class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.objects.filter(
            status=Post.PostChoices.PUBLISHED
        ).order_by("-id")[0:9]
        return context


class AboutView(TemplateView):
    template_name = "website/about.html"


class ContactUsFormView(FormView):
    form_class = ContactForm
    template_name = "website/contact.html"

    success_url = reverse_lazy("website:contact-us-view")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, "Your contact form has been submited successfully"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Your contact has not been submited successfully")
        return super().form_invalid(form)


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "website/newsletter-form.html"
    success_url = "/"

    def fom_valid(self, form):
        form.save()
        messages.success(
            self.request, "Your newsletter has been submitted successfully"
        )
        return super().form_valid(form)

    def fom_invalid(self, form):
        messages.success(
            self.request, "Your newsletter has not been submitted successfully"
        )
        return super().form_valid(form)
