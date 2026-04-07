from django.urls import path
from django.contrib.auth.views import LoginView

from users import views

app_name = "users"

urlpatterns = [
    path("sign_up/", views.UserCreateView.as_view(template_name="users/sign_up.html"), name="registration"),
    path("sign_in/", LoginView.as_view(template_name="users/sign_in.html"), name="entry"),

    path("user/<int:pk>/", views.UserDetailView.as_view(), name="profile"),
    path("user/<int:pk>/update/", views.UserDetailView.as_view(), name="profile_update"),
    path("user/<int:pk>/delete/", views.UserDeleteView.as_view(), name="profile_delete"),

    path("moderator/<int:pk>/", views.ModeratorDetailView.as_view(), name="moderator"),
    path("moderator/<int:pk>/update/", views.ModeratorDetailView.as_view(), name="moderator_update"),
    path("moderator_create/", views.ModeratorCreateView.as_view(), name="moderator_create"),
    path("moderator/<int:pk>/delete/", views.ModeratorDeleteView.as_view(), name="moderator_delete"),

    path("moderator_list/", views.ModeratorsListView.as_view(), name="moderator_list"),
    path("user_list/", views.UserListView.as_view(), name="user_list"),
]