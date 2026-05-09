from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LandingPageTests(TestCase):
    def test_landing_page_renders(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CodeArena")


class DashboardTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="reader",
            email="reader@example.com",
            password="strong-password-123",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your progress")
