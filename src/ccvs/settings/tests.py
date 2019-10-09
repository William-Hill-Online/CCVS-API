from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'USER': os.getenv('POSTGRES_USERNAME'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'TEST': {
            'NAME': os.getenv('POSTGRES_NAME')+'_test',
        },
    }
}

INSTALLED_APPS += [
    'django_nose',
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

COVER_PERC = os.getenv('COVER_PERC', '75')

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=container_scannning,core',
    '--cover-erase',
    '--cover-min-percentage='+COVER_PERC,
]
