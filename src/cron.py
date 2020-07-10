from django_cron import CronJobBase, Schedule
from django.db.models import Q
from django.utils import timezone
from .models import ScheduleMeeting

TIME_LIMIT = "720"


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'  # a unique code

    def do(self):
        # current_time = timezone.now()
        # ScheduleMeetingQs = ScheduleMeeting.objects.filter()
        pass
