from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class PreferredLanguage(models.TextChoices):
        PYTHON = "python", "Python"

    display_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    preferred_language = models.CharField(
        max_length=20,
        choices=PreferredLanguage.choices,
        default=PreferredLanguage.PYTHON,
    )

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)

# Create your models here.
