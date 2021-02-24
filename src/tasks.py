from datetime import timedelta

from celery.schedules import crontab
from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from .models import MatchedUser, PopNotification, ScheduleMeeting
from chat.models import ChatRoom


@shared_task
def unmatch_users():
    # match_with = MatchedUser.objects.filter(liked_by_me=r_user, matched='Yes').distinct()
    # match_by = MatchedUser.objects.filter(user=r_user, matched='Yes').distinct()
    # super_match_with = MatchedUser.objects.filter(super_liked_by_me=r_user, super_matched='Yes').distinct()
    # super_match_by = MatchedUser.objects.filter(user=r_user, super_matched='Yes').distinct()

    matches = MatchedUser.objects.filter(matched='Yes')
    super_matches = MatchedUser.objects.filter(super_matched='Yes')
    # meeting = ScheduleMeeting.objects.all()
    for obj in matches | super_matches:
        print(obj)
        try:
            print('inside try block')
            meeting = ScheduleMeeting.objects.filter(Q(scheduled_by=obj.user) | Q(scheduled_with=obj.user))
            print('MEETING----->>', meeting)
            if meeting:
                print('inside meeting if')
                pop_up = PopNotification.objects.filter(
                    Q(user1=meeting.scheduled_by) | Q(user2=meeting.scheduled_by) | Q(user1=meeting.scheduled_with) | Q(
                        user2=meeting.scheduled_with))
                print('POP UP----->>>', pop_up)
                if pop_up.status:
                    pass
                else:
                    print('INSIDE POP UP ELSE')
                    # if timezone.now() > obj.created_at + timedelta(days=30):
                    if timezone.now() > obj.created_at + timedelta(hours=1):
                        print('INSIDE NESTED POP UP IF')
                        meeting_obj = MatchedUser.objects.get(id=obj)
                        meeting_obj.delete()
                    else:
                        pass
            else:
                print('INSIDE MEETING ELSE')
                # if timezone.now() > obj.created_at + timedelta(days=30):
                if timezone.now() > obj.created_at + timedelta(hours=1):
                    print('INSIDE NESTED MEETING IF')
                    meeting_obj = MatchedUser.objects.get(id=obj)
                    meeting_obj.delete()
                else:
                    pass
        except Exception as e:
            print(e)
            pass
