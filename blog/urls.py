from django.urls import path

from blog import views


app_name = "catalog"

urlpatterns = [
    path("", views.HomeListView.as_view(), name="home"),
    path("", views.CatalogRedirectView.as_view(), name="home"),
]