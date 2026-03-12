from django.urls import path

from catalog import views

app_name = 'catalog'

urlpatterns = [
    path("", views.home_view, name='home'),
    path("contacts/", views.contacts_view, name='contacts'),
    path("catalogue/", views.catalogue_view, name='catalogue'),
    path("catalogue/product_create/", views.ProductCreateView.as_view(), name='product_create'),
    path("category/<int:category_id>/", views.ProductListView.as_view(), name='category'),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name='product_detail'),
    path("product/<int:pk>/update", views.ProductUpdateView.as_view(), name='product_update'),
    path("product/<int:pk>/delete", views.ProductDeleteView.as_view(), name='product_delete'),
]

