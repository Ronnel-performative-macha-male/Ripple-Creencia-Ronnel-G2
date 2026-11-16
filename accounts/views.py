from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from board.models import Rant

from .decorators import role_required
from .forms import ProfileForm, RegisterForm
from .models import User


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect("login")
        messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    """Sends each user to the dashboard for their role."""
    if request.user.role == User.MODERATOR:
        return redirect("moderator_dashboard")
    return redirect("member_dashboard")


@role_required(User.MEMBER)
def member_dashboard(request):
    context = {
        "latest_rants": Rant.objects.select_related("author", "mood")[:5],
        "my_rant_count": Rant.objects.filter(author=request.user).count(),
    }
    return render(request, "accounts/member_dashboard.html", context)


@role_required(User.MODERATOR)
def moderator_dashboard(request):
    context = {
        "total_rants": Rant.objects.count(),
        "anonymous_rants": Rant.objects.filter(is_anonymous=True).count(),
        "recent_rants": Rant.objects.select_related("author", "mood")[:5],
    }
    return render(request, "accounts/moderator_dashboard.html", context)


@login_required
def profile(request):
    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": request.user,
            "my_rants": Rant.objects.filter(author=request.user).select_related("mood")[:10],
        },
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
        messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/edit_profile.html", {"form": form})
