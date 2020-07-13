from datetime import date

from django.db.models import Q
from django.utils import timezone
from django_cron import CronJobBase, Schedule

from .models import ScheduleMeeting, MatchedUser, RegisterUser, PopNotification


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'src.my_cron_job'  # a unique code

    def do(self):
        liked_obj = MatchedUser.objects.filter(matched='Yes')
        for obj in liked_obj:
            liked_by = RegisterUser.objects.get(id=obj.user.id)
            user1 = liked_by.first_name
            liked_user = RegisterUser.objects.get(id=obj.liked_by_me.all()[0].id)
            user2 = liked_user.first_name
            schedule_obj = ScheduleMeeting.objects.filter(
                Q(scheduled_by__exact=obj.user.id) & Q(scheduled_with__exact=obj.liked_by_me.all()[0].id) & Q(
                    status__icontains='Not Completed')).values()
            if schedule_obj:
                for s_obj in schedule_obj:
                    # meeting_status = s_obj['status']
                    meeting_date = s_obj['meeting_date']
                    PopNotification.objects.create(
                        user1=user1,
                        user2=user2,
                        title='You had a meeting scheduled with {} at {}. Have you met?'.format(user2, meeting_date)
                    )
                    PopNotification.objects.create(
                        user1=user1,
                        user2=user2,
                        title='You had a meeting scheduled with {} at {}. Have you met?'.format(user1, meeting_date)
                    )
                    meeting_at = s_obj['created_at']
                    m_date = str(meeting_at.date()).split('-')
                    meeting_year = int(m_date[0])
                    meeting_month = int(m_date[1])
                    meeting_date = int(m_date[2])
                    meeting_at = date(meeting_year, meeting_month, meeting_date)
                    matched_at = str(obj.matched_at.date()).split('-')
                    matched_year = int(matched_at[0])
                    matched_month = int(matched_at[1])
                    matched_date = int(matched_at[2])
                    matched_at = date(matched_year, matched_month, matched_date)
                    delta = matched_at - meeting_at
                    if delta.days > 30:
                        obj.delete()
            else:
                today = str(timezone.now().date())
                Date = today.split('-')
                year = int(Date[0])
                month = int(Date[1])
                day = int(Date[2])
                current_day = date(year, month, day)
                matched_at = str(obj.matched_at.date()).split('-')
                matched_year = int(matched_at[0])
                matched_month = int(matched_at[1])
                matched_date = int(matched_at[2])
                matched_at = date(matched_year, matched_month, matched_date)
                delta = current_day-matched_at
                if delta.days > 30:
                    obj.delete()
