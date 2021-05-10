import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maclo.settings')

app = Celery('maclo')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.beat_schedule = {
    'unmatch_users': {
        'task': 'src.tasks.unmatch_users',
        # 'schedule': 10,
        'schedule': crontab(hour=6, minute=0),
    },
    'send_meeting_notification': {
        'task': 'src.tasks.send_meeting_notification',
        'schedule': crontab(hour=2, minute=0),
        # 'schedule': crontab(minute=11, hour='*/13'),
        # 'schedule': crontab(second=5),crontab(minute=0, hour='*/6')
        # 'schedule': 10,
        # 'args': (3, 4)
    },
}
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
