import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diip.settings')

app = Celery('diip')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    "deactivate-expired-sessions-every-15-min": {
        "task": "core.tasks.deactivate_expired_sessions",
        "schedule": crontab(minute="*/15"),
    },
}

