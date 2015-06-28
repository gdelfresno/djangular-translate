# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import LanguagesView, djangular_catalog

urlpatterns = [
    url(r'catalog/', djangular_catalog, name='catalog'),
    url(r'languages/', LanguagesView.as_view(), name='languages')
]
