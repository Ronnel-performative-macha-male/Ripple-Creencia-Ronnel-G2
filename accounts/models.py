from django.contrib.auth.models import AbstractUser
from django.db import models


class Tag(models.Model):
    MOOD = "mood"
    INTEREST = "interest"
    KIND_CHOICES = [
        (MOOD, "Mood"),
        (INTEREST, "Interest"),
    ]

    name = models.CharField(max_length=40, unique=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=INTEREST)

    class Meta:
        ordering = ["kind", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_kind_display()})"


class User(AbstractUser):
    MEMBER = "member"
    MODERATOR = "moderator"
    ROLE_CHOICES = [
        (MEMBER, "Member"),
        (MODERATOR, "Moderator"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    bio = models.TextField(max_length=300, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="users")

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.MODERATOR
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username