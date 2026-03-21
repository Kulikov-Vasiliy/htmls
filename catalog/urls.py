from django.urls import path

from catalog import views

app_name = "catalog"

urlpatterns = [
    path("", views.BlogRedirectView.as_view(), name="home"),
    path("main/", views.MainListView.as_view(), name="main"),
    path("contacts/", views.ContactsFormView.as_view(), name="contacts"),
    path("catalogue/", views.CatalogueListView.as_view(), name="catalogue"),
    path(
        "catalogue/product_create/",
        views.ProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "catalogue/category_create/",
        views.CategoryCreateView.as_view(),
        name="category_create",
    ),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path(
        "product/<int:pk>/update",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "product/<int:pk>/delete",
        views.ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path("category/<int:pk>/", views.ProductListView.as_view(), name="category"),
    path(
        "category/<int:pk>/update",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "category/<int:pk>/delete",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
]
