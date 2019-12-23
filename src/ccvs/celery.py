from __future__ import absolute_import
from __future__ import unicode_literals

from celery import Celery
from django.conf import settings


db = settings.DATABASES['default']
broker = f"sqla+postgresql://{db['USER']}:{db['PASSWORD']}" \
    f"@{db['HOST']}:{db['PORT']}/{db['NAME']}"
app = Celery('ccvs', broker=broker, result_backend='sqla+postgresql')

app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle']
)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
