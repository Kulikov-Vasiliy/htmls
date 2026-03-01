from django.shortcuts import render, get_object_or_404
from catalog.models import Product, Category
from django.utils import timezone


# Create your views here.
def base_view(request):
    """Контроллер позволяет считывать базовую страницу"""
    return render(request, 'base.html')

def home_view(request):
    """Контроллер позволяет наполнять базовую страницу: общими товарами"""
    page_name = "home"
    products = Product.objects.all()
    context = {"products": products, "page_name": page_name}
    return render(request, 'home.html', context)


def contacts_view(request):
    """Контроллер позволяет наполнять базовую страницу: контактами"""
    page_name = "contacts"
    context = {"page_name": page_name}
    return render(request, 'contacts.html', context)


def category_view(request, pk):
    """Контроллер позволяет наполнять базовую страницу: категорией"""
    page_name = "category"
    current_category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=current_category)
    context = {
        "category": current_category,
        "products": products,
        "page_name": page_name
    }
    return render(request, 'category.html', context)


def catalogue_view(request):
    """Контроллер позволяет наполнять базовую страницу: каталогом"""
    page_name = "catalogue"
    catalogue = Category.objects.all()
    context = {"catalogue": catalogue, "page_name": page_name}
    return render(request, 'catalogue.html', context)
