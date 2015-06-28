# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import shutil

from django.test import TestCase, RequestFactory
from django.utils import six
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware
from django.utils.translation import get_language_from_request
from django.core.management import call_command
from django.conf import settings
from django.core.management.commands import compilemessages

from ngtranslate.views import LanguagesView


class TranslationTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_languages(self):

        request = self.factory.get('/languages/')
        response = LanguagesView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        response_content = response.content
        if six.PY3:
            response_content = str(response_content, encoding='utf8')

        expected = {u'current': 0,
                    u'languages': [{u'code': u'en', u'name': u'English'},
                                   {u'code': u'ru', u'name': u'Russian'},
                                   {u'code': u'de', u'name': u'German'}]}

        self.assertJSONEqual(response_content, expected)

    def test_set_language(self):

        request = self.factory.post('/languages/',
                                    json.dumps({'lang': 'ru'}),
                                    content_type="application/json")
        smiddleware = SessionMiddleware()
        lmiddleware = LocaleMiddleware()
        smiddleware.process_request(request)
        lmiddleware.process_request(request)
        request.session.save()

        response = LanguagesView.as_view()(request)

        lmiddleware.process_response(request, response)

        self.assertEqual(response.status_code, 200)

        response_content = response.content

        if six.PY3:
            response_content = str(response_content, encoding='utf8')

        self.assertJSONEqual(response_content, {u'success': True})

        self.assertEqual(response['Content-Language'], u'ru')

    def test_makemessages(self):
        call_command('makemessages', domain='djangular', locale=('ru', 'de',))
        locale_path = settings.LOCALE_PATHS[0]
        ru_locale = os.path.join(locale_path, 'ru/LC_MESSAGES/djangular.po')
        de_locale = os.path.join(locale_path, 'de/LC_MESSAGES/djangular.po')
        assert os.path.exists(ru_locale) == 1
        assert os.path.exists(de_locale) == 1
        call_command('makemessages', locale=('ru', 'de',))
        ru_locale = os.path.join(locale_path, 'ru/LC_MESSAGES/django.po')
        de_locale = os.path.join(locale_path, 'de/LC_MESSAGES/django.po')
        assert os.path.exists(ru_locale) == 1
        assert os.path.exists(de_locale) == 1
        shutil.rmtree(locale_path)

    def test_catalog(self):
        response = self.client.get('/catalog/?lang=ru')
        self.assertEqual(response.status_code, 200)
        response_content = response.content

        if six.PY3:
            response_content = str(response_content, encoding='utf8')

        self.assertJSONEqual(response_content, {})

        locale_path = settings.LOCALE_PATHS[0]
        os.makedirs(os.path.join(locale_path, 'ru/LC_MESSAGES'))
        ru_locale = os.path.join(locale_path, 'ru/LC_MESSAGES/djangular.po')
        tst_locale = os.path.join(settings.BASE_DIR,
                                  'ngtranslate/tests/djangular.tst.po')
        shutil.copyfile(tst_locale, ru_locale)
        os.environ['DJANGO_SETTINGS_MODULE']='settings.py'
        call_command('compilemessages')

        response = self.client.get('/catalog/?lang=ru')
        self.assertEqual(response.status_code, 200)
        response_content = response.content

        if six.PY3:
            response_content = str(response_content, encoding='utf8')

        self.assertJSONEqual(response_content, 
                             {u'ngTranslate test': u'ngTranslate тест'})
        shutil.rmtree(locale_path)


