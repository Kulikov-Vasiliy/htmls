from config.settings import CACHE_ENABLED
from django.core.cache import cache
from catalog.models import Product


def get_products_from_cache(queryset, cache_key):
    """Получение данных из кэша, если его нет-из бд"""
    if not CACHE_ENABLED:
        return queryset
    else:
        products = cache.get(cache_key)
        if products is not None:
            return products
        else:
            products = list(queryset)
            cache.set(cache_key, products)
            return products

