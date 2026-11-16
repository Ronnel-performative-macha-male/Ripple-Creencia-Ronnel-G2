from django.conf import settings
from django.db import models


class Rant(models.Model):
    """A post on the Rant Board. Can be public or anonymous."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rants",
    )
    mood = models.ForeignKey(
        "accounts.Tag",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"kind": "mood"},
        related_name="rants",
    )
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField(max_length=1000)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Rant #{self.pk} by {self.author}"
