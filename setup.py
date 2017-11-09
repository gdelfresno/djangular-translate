import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djangular-translate',
    version='0.0.1',
    packages=['ngtranslate'],
    include_package_data=True,
    license='BSD License',
    description='Django module to implement i18n support for angularJS applications.',
    long_description=README,
    url='https://github.com/magnitronus/djangular-translate',
    author='Anton Lysenkov',
    author_email='aalisenkov@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    requires=['django']
)
