from django.urls import path

from catalog import views

app_name = 'catalog'

urlpatterns = [
    path("", views.home_view, name='home'),
    path("contacts/", views.contacts_view, name='contacts'),
    path("catalogue/", views.catalogue_view, name='catalogue'),
    path("category/<int:pk>/", views.category_view, name='category'),
    path("product/<int:pk>/", views.product_view, name='product'),
]
