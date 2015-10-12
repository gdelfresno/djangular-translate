# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import LanguagesView, djangular_catalog

urlpatterns = [
    url(r'catalog/', djangular_catalog, name='catalog'),
    url(r'languages/', csrf_exempt(LanguagesView.as_view()), name='languages')
]
