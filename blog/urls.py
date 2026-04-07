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
]