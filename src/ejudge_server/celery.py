import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ejudge_server.site.settings')
app = Celery('ejudge-server', broker='redis://localhost//')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
