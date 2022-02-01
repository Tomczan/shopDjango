import os
from celery import Celery

# ustawienie domyslnego modulu ustawien Django dla programu 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopDjango.settings')

app = Celery('shopDjango')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()