from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Tag, User

from .forms import RantForm
from .models import Rant

PER_PAGE = 10


def decorate(rants, user):
    """Attach per-user display flags to each rant (what this user may see or do)."""
    rants = list(rants)
    is_mod = user.role == User.MODERATOR
    for rant in rants:
        rant.is_mine = rant.author_id == user.id
        rant.can_edit = rant.is_mine
        rant.can_delete = rant.is_mine or is_mod
        # Moderators can see who wrote an anonymous rant (needed to review reports).
        if rant.is_anonymous:
            rant.shown_author = f"Anonymous (posted by {rant.author.username})" if is_mod else "Anonymous"
            if rant.is_mine:
                rant.shown_author = "You (anonymous)"
        else:
            rant.shown_author = "You" if rant.is_mine else rant.author.username
        rant.was_edited = (rant.updated_at - rant.created_at).total_seconds() > 60
    return rants


def _all_rants():
    return Rant.objects.select_related("author", "mood").order_by("-created_at", "-id")


@login_required
def rant_list(request):
    qs = _all_rants()
    mood_id = request.GET.get("mood", "")
    if mood_id.isdigit():
        qs = qs.filter(mood_id=int(mood_id))
    page = Paginator(qs, PER_PAGE).get_page(request.GET.get("page"))
    page.object_list = decorate(page.object_list, request.user)
    return render(
        request,
        "board/rant_list.html",
        {
            "page": page,
            "moods": Tag.objects.filter(kind=Tag.MOOD),
            "selected_mood": mood_id,
            "heading": "Rant Board",
        },
    )


@login_required
def my_rants(request):
    qs = _all_rants().filter(author=request.user)
    page = Paginator(qs, PER_PAGE).get_page(request.GET.get("page"))
    page.object_list = decorate(page.object_list, request.user)
    return render(
        request,
        "board/rant_list.html",
        {"page": page, "moods": None, "selected_mood": "", "heading": "My rants"},
    )


@login_required
def rant_detail(request, pk):
    rant = decorate([get_object_or_404(_all_rants(), pk=pk)], request.user)[0]
    return render(request, "board/rant_detail.html", {"rant": rant})


@login_required
def rant_create(request):
    if request.method == "POST":
        form = RantForm(request.POST, user=request.user)
        if form.is_valid():
            rant = form.save(commit=False)
            rant.author = request.user
            rant.save()
            messages.success(request, "Your rant has been posted.")
            return redirect("board:detail", pk=rant.pk)
        messages.error(request, "Please fix the errors below.")
    else:
        form = RantForm(user=request.user)
    return render(request, "board/rant_form.html", {"form": form, "mode": "Post a rant"})


@login_required
def rant_edit(request, pk):
    rant = get_object_or_404(Rant, pk=pk)
    if rant.author_id != request.user.id:
        raise PermissionDenied  # only the author can edit
    if request.method == "POST":
        form = RantForm(request.POST, instance=rant, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your rant has been updated.")
            return redirect("board:detail", pk=rant.pk)
        messages.error(request, "Please fix the errors below.")
    else:
        form = RantForm(instance=rant, user=request.user)
    return render(request, "board/rant_form.html", {"form": form, "mode": "Edit rant"})


@login_required
def rant_delete(request, pk):
    rant = get_object_or_404(Rant, pk=pk)
    if rant.author_id != request.user.id and request.user.role != User.MODERATOR:
        raise PermissionDenied  # author or moderator only
    if request.method == "POST":
        rant.delete()
        messages.success(request, "The rant has been deleted.")
        return redirect("board:list")
    return render(request, "board/rant_confirm_delete.html", {"rant": rant})
