from celery import Celery
from django.conf import settings

db = settings.DATABASES['default']
broker = (
    f"sqla+postgresql://{db['USER']}:{db['PASSWORD']}"
    f"@{db['HOST']}:{db['PORT']}/{db['NAME']}"
)
app = Celery('ccvs', broker=broker, result_backend='sqla+postgresql')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
