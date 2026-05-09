from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_user_defaults_display_name_to_username(self):
        user = get_user_model().objects.create_user(
            username="mohit",
            email="mohit@example.com",
            password="strong-password-123",
        )

        self.assertEqual(user.display_name, "mohit")
        self.assertEqual(user.preferred_language, "python")


class AuthPagesTests(TestCase):
    def test_signup_page_renders(self):
        response = self.client.get(reverse("accounts:signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create your account")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 302)
