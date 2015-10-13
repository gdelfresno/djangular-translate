djangular-translate
=====

Django module to implement i18n translations support for angularJS applications. 
Work together with angular module [ng-django-translate](https://github.com/magnitronus/ng-django-translate)

Installation
=====================

1) pip install git+https://github.com/magnitronus/djangular-translate.git
2) Add 'ngtranslate' to INSTALLED_APPS in settings.py:

    INSTALLED_APPS = (...
                      'ngtranslate',
                      ...
                     )
3) Define LOCALE_PATHS in settings.py:

    LOCALE_PATHS = (
        os.path.join(BASE_DIR, '../locale'),
    )
    
4) Add path to ngtranslate to your urlpatterns in urls.py:

    urlpatterns = [
        ...
        url(r'^i18n/', include('ngtranslate.urls')),
        ...
    ]
    
Using
==============================

Make i18n messages
------------------

Ngtranslate overrides native django management "makemessages" command. For making messages from angular directives, your angular static templates must be placed in django templates folder (you can use symbolic links for this). For make messages try use "djangular" domain:

      python manage.py makemessages -d djangular -s -l <your_locale>
      

    
