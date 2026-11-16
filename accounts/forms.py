from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Tag, User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    # (placeholder, autocomplete) for each field, used by the sign-up UI.
    FIELD_HINTS = {
        "first_name": ("First name", "given-name"),
        "last_name": ("Last name", "family-name"),
        "username": ("Choose a username", "username"),
        "email": ("you@example.com", "email"),
        "password1": ("Create a password", "new-password"),
        "password2": ("Re-enter your password", "new-password"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, (placeholder, autocomplete) in self.FIELD_HINTS.items():
            self.fields[name].widget.attrs.update(
                {"placeholder": placeholder, "autocomplete": autocomplete}
            )
        self.fields["password2"].label = "Confirm password"
        self.fields["password1"].help_text = (
            "At least 8 characters. Not too common, not all numbers, "
            "and not too similar to your name or email."
        )
        self.fields["password2"].help_text = ""
        # Start typing at the top of the form (Django focuses username by default).
        self.fields["username"].widget.attrs.pop("autofocus", None)
        self.fields["first_name"].widget.attrs["autofocus"] = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(AuthenticationForm):
    """Login form with placeholders and browser autofill hints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Your username", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Your password", "autocomplete": "current-password"}
        )


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    bio = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Up to 300 characters.",
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Mood / interest tags",
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "bio", "tags")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email