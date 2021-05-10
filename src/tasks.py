import datetime
from datetime import timedelta

import pytz
from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from adminpanel.models import UserNotification, User
from fcm_notification import send_another
from .models import MatchedUser, PopNotification, ScheduleMeeting

utc = pytz.UTC


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
            meetings = ScheduleMeeting.objects.filter(Q(scheduled_by=obj.user) | Q(scheduled_with=obj.user))
            print('MEETING----->>', meetings)
            if len(meetings) > 0:
                print('inside meeting if')
                for meeting in meetings:
                    pop_ups = PopNotification.objects.filter(
                        Q(user1=meeting.scheduled_by) | Q(user2=meeting.scheduled_by) | Q(
                            user1=meeting.scheduled_with) | Q(
                            user2=meeting.scheduled_with))
                    print('POP UP----->>>', pop_ups)
                    for pop_up in pop_ups:
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
                    # print('INSIDE NESTED MEETING IF')
                    meeting_obj = MatchedUser.objects.get(id=obj)
                    meeting_obj.delete()
                else:
                    pass
        except Exception as e:
            print(e)
            pass


def send_meeting_notification():
    matches = MatchedUser.objects.filter(matched='Yes')
    super_matches = MatchedUser.objects.filter(super_matched='Yes')
    for obj in matches | super_matches:
        print(obj)
        meetings = ScheduleMeeting.objects.filter(Q(scheduled_by=obj.user) | Q(scheduled_with=obj.user))
        for meeting in meetings:
            if meeting.meeting_date == timezone.now().date():
                UserNotification.objects.create(
                    to=User.objects.get(email=meeting.scheduled_by.email),
                    title='Meeting Schedule',
                    body="You have a meeting scheduled today with " + meeting.scheduled_with.first_name,
                    extra_text=f'{meeting.scheduled_with.id}'
                )
                fcm_token = User.objects.get(email=meeting.scheduled_by.email).device_token
                try:
                    title = "Meeting Schedule"
                    body = "You have a meeting scheduled today with " + meeting.scheduled_with.first_name
                    message_type = "meeting"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
                UserNotification.objects.create(
                    to=User.objects.get(email=meeting.scheduled_with.email),
                    title='Meeting Schedule',
                    body="You have a meeting scheduled today with " + meeting.scheduled_by.first_name,
                    extra_text=f'{meeting.scheduled_by.id}'
                )
                fcm_token = User.objects.get(email=meeting.scheduled_with.email).device_token
                try:
                    title = "Meeting Schedule"
                    body = "You have a meeting scheduled today with " + meeting.scheduled_by.first_name
                    message_type = "meeting"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
            elif datetime.datetime.now() == meeting.meeting_date - datetime.timedelta(hours=24):
                UserNotification.objects.create(
                    to=User.objects.get(email=meeting.scheduled_by.email),
                    title='Meeting Schedule',
                    body="You have a meeting scheduled tomorrow with " + meeting.scheduled_with.first_name,
                    extra_text=f'{meeting.scheduled_with.id}'
                )
                fcm_token = User.objects.get(email=meeting.scheduled_by.email).device_token
                try:
                    title = "Meeting Schedule"
                    body = "You have a meeting scheduled tomorrow with " + meeting.scheduled_with.first_name
                    message_type = "meeting"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
                UserNotification.objects.create(
                    to=User.objects.get(email=meeting.scheduled_with.email),
                    title='Meeting Schedule',
                    body="You have a meeting scheduled tomorrow with " + meeting.scheduled_by.first_name,
                    extra_text=f'{meeting.scheduled_by.id}'
                )
                fcm_token = User.objects.get(email=meeting.scheduled_with.email).device_token
                try:
                    title = "Meeting Schedule"
                    body = "You have a meeting scheduled tomorrow with " + meeting.scheduled_by.first_name
                    message_type = "meeting"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
            else:
                pass
