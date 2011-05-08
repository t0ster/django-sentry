#!/usr/bin/env python
import logging
import sys
from os.path import dirname, abspath, join
from optparse import OptionParser

logging.getLogger('sentry').addHandler(logging.StreamHandler())

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASES={
            'default': {
                'ENGINE': 'sqlite3',
            },
        },
        # HACK: this fixes our threaded runserver remote tests
        # DATABASE_NAME='test_sentry',
        # TEST_DATABASE_NAME='test_sentry',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django.contrib.sites',

            # Included to fix Disqus' test Django which solves IntegrityMessage case
            'django.contrib.contenttypes',

            'south',
            'djcelery', # celery client
            # 'haystack',

            'sentry',
            'sentry.client.django',
            'sentry.client.celery',

            # included plugin tests
            # 'sentry.plugins.sentry_servers',
            # 'sentry.plugins.sentry_urls',
            # 'sentry.plugins.sentry_redmine',

            # No fucking idea why I have to do this
            'sentry.tests',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
        SITE_ID=1,
        BROKER_HOST="localhost",
        BROKER_PORT=5672,
        BROKER_USER="guest",
        BROKER_PASSWORD="guest",
        BROKER_VHOST="/",
        CELERY_ALWAYS_EAGER=True,
        SENTRY_THRASHING_LIMIT=0,
        TEMPLATE_DEBUG=True,
        # HAYSTACK_SITECONF='sentry.search_indexes',
        # HAYSTACK_SEARCH_ENGINE='whoosh',
        # SENTRY_SEARCH_ENGINE='whoosh',
        # SENTRY_SEARCH_OPTIONS={
        #     'path': join(dirname(__file__), 'sentry_index'),
        # },
    )
    import djcelery
    djcelery.setup_loader()

from django.test.simple import run_tests

def runtests(failfast=False, *test_args):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['sentry']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=False, failfast=failfast)
    sys.exit(failures)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true', default=False, dest='failfast')

    (options, args) = parser.parse_args()

    runtests(*args, failfast=options.failfast)
