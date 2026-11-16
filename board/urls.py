from django.urls import path

from . import views

app_name = "board"

urlpatterns = [
    path("", views.rant_list, name="list"),
    path("mine/", views.my_rants, name="mine"),
    path("new/", views.rant_create, name="create"),
    path("<int:pk>/", views.rant_detail, name="detail"),
    path("<int:pk>/edit/", views.rant_edit, name="edit"),
    path("<int:pk>/delete/", views.rant_delete, name="delete"),
]
