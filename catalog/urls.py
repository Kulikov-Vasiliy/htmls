from django.urls import path

from catalog import views

app_name = 'catalog'

urlpatterns = [
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name='product'),
    # path("category/<int:pk>/", views.category_view, name='category'),
    path("category/<int:category_id>/", views.ProductListView.as_view(), name='category'),
    # path("product/<int:category_id>/", views.ProductListView.as_view(), name='product'),
    path("", views.home_view, name='home'),
    path("contacts/", views.contacts_view, name='contacts'),
    path("catalogue/", views.catalogue_view, name='catalogue'),

]
