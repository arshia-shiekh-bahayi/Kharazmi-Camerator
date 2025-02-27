from django.test import TestCase
from apps.website.models import Contact, Newsletter


class TestContactModel(TestCase):
    def setUp(self):
        pass

    def test_contact_model(self):
        self.contact = Contact.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test Message",
        )
        self.assertEqual(self.contact.name, "Test User")
        self.assertEqual(self.contact.email, "test@example.com")
        self.assertEqual(self.contact.subject, "Test Subject")
        self.assertEqual(self.contact.message, "Test Message")


class TestNewsletterModel(TestCase):
    def setUp(self):
        pass

    def test_newsletter_model(self):
        self.newsletter = Newsletter.objects.create(email="test@example.com")
        self.assertEqual(self.newsletter.email, "test@example.com")
