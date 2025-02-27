from django.test import TestCase
from apps.service.models import Service


class TestServiceModel(TestCase):
    def setUp(self):
        pass

    def test_service_model(self):
        self.service = Service.objects.create(
            title="Test Service",
            slug="test-service",
            description="Test Description",
            number_of_photos=20,
            thumbnail="services/images/img8.jpg",
            processing=Service.ProcessingType.FINISHED,
            camera=Service.CameraType.PROFESSIONAL,
            resolution=Service.ResolutionType.MP108,
            term=14,
            price=20,
            status=Service.ServiceChoices.DRAFT,
        )

        self.assertEqual(self.service.title, "Test Service")
        self.assertEqual(self.service.slug, "test-service")
        self.assertEqual(self.service.description, "Test Description")
        self.assertEqual(self.service.number_of_photos, 20)
        self.assertEqual(self.service.thumbnail.name, "services/images/img8.jpg")
        self.assertEqual(self.service.processing, Service.ProcessingType.FINISHED)
        self.assertEqual(self.service.camera, Service.CameraType.PROFESSIONAL)
        self.assertEqual(self.service.resolution, Service.ResolutionType.MP108)
        self.assertEqual(self.service.term, 14)
        self.assertEqual(self.service.price, 20)
        self.assertEqual(self.service.status, Service.ServiceChoices.DRAFT)
