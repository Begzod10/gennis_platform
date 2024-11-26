from django.urls import get_resolver, URLPattern, URLResolver

def count_urls(urlpatterns=None, depth=0):
    if urlpatterns is None:
        urlpatterns = get_resolver().url_patterns

    total_count = 0

    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):  # It's a simple URL pattern
            total_count += 1
        elif isinstance(pattern, URLResolver):  # It's an include
            total_count += count_urls(pattern.url_patterns, depth + 2)

    return total_count

# URLlarni hisoblash uchun funktsiyani chaqirish
total_urls = count_urls()
