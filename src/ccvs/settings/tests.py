from .base import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME'),  # noqa: F405
        'HOST': os.getenv('POSTGRES_HOST'),  # noqa: F405
        'PORT': os.getenv('POSTGRES_PORT', '5432'),  # noqa: F405
        'USER': os.getenv('POSTGRES_USERNAME'),  # noqa: F405
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),  # noqa: F405
        'TEST': {
            'NAME': os.getenv('POSTGRES_NAME')+'_test',  # noqa: F405
        },
    }
}

INSTALLED_APPS += [  # noqa: F405
    'django_nose',
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

COVER_PERC = os.getenv('COVER_PERC', '75')  # noqa: F405

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=container_scanning',
    '--cover-min-percentage='+COVER_PERC,
    '--verbosity=2',
]
