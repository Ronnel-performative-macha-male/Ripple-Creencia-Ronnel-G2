from django import forms
from django.utils import timezone

from .models import Rant

MIN_LENGTH = 10
DAILY_LIMIT = 10


class RantForm(forms.ModelForm):
    class Meta:
        model = Rant
        fields = ("title", "mood", "content", "is_anonymous")
        labels = {
            "title": "Title (optional)",
            "mood": "How are you feeling? (optional)",
            "content": "What's on your mind?",
            "is_anonymous": "Post anonymously",
        }
        widgets = {"content": forms.Textarea(attrs={"rows": 6, "maxlength": 1000})}
        help_texts = {
            "content": f"{MIN_LENGTH} to 1000 characters.",
            "is_anonymous": "Other members will see 'Anonymous' instead of your username.",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["mood"].empty_label = "Choose a mood"
        self.fields["mood"].label_from_instance = lambda tag: tag.name

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if len(content) < MIN_LENGTH:
            raise forms.ValidationError(f"Please write at least {MIN_LENGTH} characters.")
        return content

    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean(self):
        cleaned = super().clean()
        # Business rule: limit new rants per day (editing is not limited).
        if self.instance.pk is None and self.user is not None:
            start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
            today = Rant.objects.filter(author=self.user, created_at__gte=start).count()
            if today >= DAILY_LIMIT:
                raise forms.ValidationError(
                    f"You can post up to {DAILY_LIMIT} rants per day. Take a break and come back tomorrow."
                )
        return cleaned
