from django.http import JsonResponse
from django.utils.translation import (
    check_for_language, to_locale,
    get_language_from_request
)
from django.views.i18n import get_javascript_catalog


def djangular_catalog(request):
    locale = to_locale(get_language_from_request(request))

    if request.GET and 'lang' in request.GET:
        if check_for_language(request.GET['lang']):
            locale = to_locale(request.GET['lang'])
    django_catalog, plural = get_javascript_catalog(locale, 'django', [])
    angular_catalog, plural = get_javascript_catalog(locale, 'djangular', [])
    django_catalog.update(angular_catalog)
    return JsonResponse(django_catalog)
