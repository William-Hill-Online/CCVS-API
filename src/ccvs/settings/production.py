import os

from .base import *  # noqa

ROOT_URLCONF = 'ccvs.urls.production'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'USER': os.getenv('POSTGRES_USERNAME'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    }
}
