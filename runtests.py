import os, sys
import django
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, 
                            'ngtranslate/tests/templates/ngtranslate/')
LOCALE_PATH = os.path.join(BASE_DIR, 
                           'ngtranslate/tests/locale')

settings.configure(DEBUG=True,
                   BASE_DIR=BASE_DIR,
                   TEMPLATE_DIRS=(TEMPLATE_DIR,),
                   LOCALE_PATHS=(LOCALE_PATH,),
                   DATABASES={
                              'default': {
                                        'ENGINE': 'django.db.backends.sqlite3',
                                        }
                   },
                   LANGUAGES = (
                       ('en', _('English')),
                       ('ru', _('Russian')),
                       ('de', _('German')),
                   ),
                   ROOT_URLCONF='ngtranslate.urls',
                   INSTALLED_APPS=('django.contrib.auth',
                                   'django.contrib.contenttypes',
                                   'django.contrib.sessions',
                                   'django.contrib.admin',
                                   'ngtranslate',),
                   LANGUAGE_CODE = 'en-us',
                   USE_I18N = True)

try:
    # Django <= 1.8
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    # Django >= 1.8
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)


failures = test_runner.run_tests(['ngtranslate.tests'])

if failures:
    sys.exit(failures)
