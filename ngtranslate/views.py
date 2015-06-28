# -*- coding: utf-8 -*-
import json

from django.http import JsonResponse
from django.conf import settings
from django.views.i18n import get_javascript_catalog
from django.views.generic import View
from django.utils.translation import (
    check_for_language, get_language, to_locale,
    get_language_from_request, activate
)


def djangular_catalog(request):
    locale = to_locale(get_language_from_request(request))

    if request.GET and 'lang' in request.GET:
        if check_for_language(request.GET['lang']):
            locale = to_locale(request.GET['lang'])
    catalog, plural = get_javascript_catalog(locale, 'djangular',
                                             ['django.conf'])
    return JsonResponse(catalog)


class LanguagesView(View):

    def get(self, request):
        result = {'languages': [], 'current': 0}
        current = get_language_from_request(request)
        idx = 0
        for idx, item in enumerate(settings.LANGUAGES):
            if item[0] == current:
                result['current'] = idx
            result['languages'].append({'code': item[0],
                                        'name': unicode(item[1])})
        return JsonResponse(result)

    def post(self, request):
        result = {'success': False}
        request_data = json.loads(request.body)
        language = request_data.get('lang')
        if language:
            activate(language)
            request.session['django_language'] = get_language()
            result = {'success': True}
        return JsonResponse(result)
