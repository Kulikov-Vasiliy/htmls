from django.urls import path

from blog import views


app_name = "blog"


urlpatterns = [
    path("", views.HomeListView.as_view(), name="home"),
    path("category/<int:pk>/", views.CategoriesDetailView.as_view(), name="category"),

    path("main/", views.CatalogRedirectView.as_view(), name="main"),

    path("post/create/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),

    path("post/<int:pk>/comments/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("post/<int:pk>/comments/create/", views.CommentCreateView.as_view(), name="comment_create"),
    path("post/<int:post_pk>/comments/<int:comm_pk>/update/", views.CommentUpdateView.as_view(), name="comment_update"),

    path("sign_up/", views.UserCreateView.as_view(), name="registration"),
    path("sign_in/", views.SignInFormView.as_view(), name="entry"),

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