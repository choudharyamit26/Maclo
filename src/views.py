import json
import os
import shutil
from datetime import timedelta

import urllib3
from django.contrib.gis.measure import Distance
import instaloader
import requests
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework
from fcm_django.models import FCMDevice
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from adminpanel.models import UserNotification, Transaction, UserHeartBeatsPerDay, ExtraHeartBeats, SubscriptionStatus
from .fcm_notification import send_another
from .models import UserInstagramPic, UserDetail, RegisterUser, MatchedUser, RequestMeeting, ScheduleMeeting, Feedback, \
    AboutUs, ContactUs, SubscriptionPlans, ContactUsQuery, DeactivateAccount, BlockedUsers, PopNotification, \
    FeedbackWithoutStars
from .serializers import (UserDetailSerializer, UserInstagramSerializer, RegisterSerializer,
                          MatchedUserSerializer, LikeSerializer, DeleteMatchSerializer, SuperLikeSerializer,
                          RequestMeetingSerializer, ScheduleMeetingSerializer, FeedbackSerializer, ContactUsSerializer,
                          AboutUsSerializer, MeetingStatusSerializer, PopUpNotificationSerializer,
                          SubscriptionPlanSerializer, DeleteSuperMatchSerializer, SearchSerializer,
                          GetInstagramPicSerializer, ShowInstaPics, AuthTokenSerializer,
                          FacebookSerializer, GmailSerializer)

# from adminpanel.models import UserNotification

User = get_user_model()


class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        phone_number = self.request.data['phone_number']
        device_token = self.request.data['device_token']
        x = {}
        try:
            user = User.objects.get(phone_number=int(phone_number))
            if user:
                user.device_token = device_token
                user.save()
                token = Token.objects.get_or_create(user=user)
                user_data = RegisterUser.objects.get(phone_number=phone_number)
                user_detail = UserDetail.objects.get(phone_number=user_data)
                pic_1 = ''
                pic_2 = ''
                pic_3 = ''
                pic_4 = ''
                pic_5 = ''
                pic_6 = ''
                pic_7 = ''
                pic_8 = ''
                pic_9 = ''
                if user_data.pic_1:
                    pic_1 = user_data.pic_1.url
                else:
                    pic_1 = ''
                if user_data.pic_2:
                    pic_2 = user_data.pic_2.url
                else:
                    pic_2 = ''
                if user_data.pic_3:
                    pic_3 = user_data.pic_3.url
                else:
                    pic_3 = ''
                if user_data.pic_4:
                    pic_4 = user_data.pic_4.url
                else:
                    pic_4 = ''
                if user_data.pic_5:
                    pic_5 = user_data.pic_5.url
                else:
                    pic_5 = ''
                if user_data.pic_6:
                    pic_6 = user_data.pic_6.url
                else:
                    pic_6 = ''
                # if user_data.pic_7:
                #     pic_7 = user_data.pic_8.url
                # else:
                #     pic_7 = ''
                # if user_data.pic_8:
                #     pic_8 = user_data.pic_8.url
                # else:
                #     pic_8 = ''
                # if user_data.pic_9:
                #     pic_9 = user_data.pic_9.url
                # else:
                #     pic_9 = ''
                Data = {
                    "id": user_data.id,
                    "email": user_data.email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "phone_number": user_data.phone_number,
                    "gender": user_data.gender,
                    "date_of_birth": user_data.date_of_birth,
                    # "job_profile": user_data.job_profile,
                    # "company_name": user_data.company_name,
                    # "qualification": user_data.qualification,
                    # "relationship_status": user_data.relationship_status,
                    # "interests": user_data.interests,
                    # "fav_quote": user_data.fav_quote,
                    "pic_1": pic_1,
                    "pic_2": pic_2,
                    "pic_3": pic_3,
                    "pic_4": pic_4,
                    "pic_5": pic_5,
                    "pic_6": pic_6,
                    # "pic_7": pic_7,
                    # "pic_8": pic_8,
                    # "pic_9": pic_9,
                    "discovery_lat": user_detail.discovery[0],
                    "discovery_lang": user_detail.discovery[1],
                    "distance_range": user_detail.distance_range,
                    "min_age_range": user_detail.min_age_range,
                    "max_age_range": user_detail.max_age_range,
                    "interested": user_detail.interest
                }
                r_user = RegisterUser.objects.get(email=user.email)
                account = DeactivateAccount.objects.get(user=r_user)
                if account.deactivated:
                    account.deactivated = False
                    account.save()
                    user_detail.deactivated = False
                    user_detail.save()
                print(token)
                print(token[0].key)
                return Response(
                    {'token': token[0].key, 'data': Data, 'deactivated': account.deactivated, 'status': HTTP_200_OK})
        except Exception as e:
            x = {"Error": str(e)}
            return Response({'message': x['Error'], "status": HTTP_400_BAD_REQUEST})
        return Response({'message': x['Error'], "status": HTTP_400_BAD_REQUEST})


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        serializer = RegisterSerializer(data=self.request.data)
        first_name = self.request.data['first_name']
        last_name = self.request.data['last_name']
        phone_number = self.request.data['phone_number']
        gender = self.request.data['gender']
        date_of_birth = self.request.data['date_of_birth']
        device_token = self.request.data['device_token']
        # job_profile = self.request.data['job_profile']
        # company_name = self.request.data['company_name']
        email = self.request.data['email']
        height = self.request.data['height']
        # qualification = self.request.data['qualification']
        # relationship_status = self.request.data['relationship_status']
        # interests = self.request.data['interests']
        # fav_quote = self.request.data['fav_quote']
        # liked_by = RegisterUser.objects.filter(id=phone_number)
        # superliked_by = RegisterUser.objects.filter(id=phone_number)
        pic_1 = self.request.data['pic_1']
        pic_2 = self.request.data['pic_2']
        pic_3 = self.request.data['pic_3']
        pic_4 = self.request.data['pic_4']
        pic_5 = self.request.data['pic_5']
        pic_6 = self.request.data['pic_6']
        # pic_7 = self.request.data['pic_7']
        # pic_8 = self.request.data['pic_8']
        # pic_9 = self.request.data['pic_9']
        lat = self.request.data['lat']
        lang = self.request.data['lang']
        user_qs = RegisterUser.objects.filter(
            phone_number__iexact=phone_number)
        if user_qs.exists():
            serializer.is_valid(raise_exception=True)
            return Response(
                {"Phone number": "User with this phone number already exists.", "status": HTTP_400_BAD_REQUEST})
        if serializer.is_valid():
            user = RegisterUser.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                gender=gender,
                date_of_birth=date_of_birth,
                height=height,
                # job_profile=job_profile,
                # company_name=company_name,
                # qualification=qualification,
                # relationship_status=relationship_status,
                # interests=interests,
                # fav_quote=fav_quote,
                # liked_by=liked_by,
                # superliked_by=superliked_by,
                pic_1=pic_1,
                pic_2=pic_2,
                pic_3=pic_3,
                pic_4=pic_4,
                pic_5=pic_5,
                pic_6=pic_6,
                # pic_7=pic_7,
                # pic_8=pic_8,
                # pic_9=pic_9
            )
            user_detail = UserDetail.objects.create(
                phone_number=user,
                discovery=fromstr(f'POINT({lang} {lat})', srid=4326)
            )
            us_obj = User.objects.create(
                email=email,
                phone_number=phone_number,
                device_token=device_token
            )
            us_obj.set_password(phone_number)
            us_obj.save()
            DeactivateAccount.objects.create(
                user=user
            )
            # for x in liked_by:
            #     RegisterUser.liked_by.add(x)
            # for y in superliked_by:
            #     RegisterUser.superliked_by.add(y)
            user_data = RegisterUser.objects.get(phone_number=phone_number)
            pic_1 = ''
            pic_2 = ''
            pic_3 = ''
            pic_4 = ''
            pic_5 = ''
            pic_6 = ''
            pic_7 = ''
            pic_8 = ''
            pic_9 = ''
            if user_data.pic_1:
                pic_1 = user_data.pic_1.url
            else:
                pic_1 = ''
            if user_data.pic_2:
                pic_2 = user_data.pic_2.url
            else:
                pic_2 = ''
            if user_data.pic_3:
                pic_3 = user_data.pic_3.url
            else:
                pic_3 = ''
            if user_data.pic_4:
                pic_4 = user_data.pic_4.url
            else:
                pic_4 = ''
            if user_data.pic_5:
                pic_5 = user_data.pic_5.url
            else:
                pic_5 = ''
            if user_data.pic_6:
                pic_6 = user_data.pic_6.url
            else:
                pic_6 = ''
            # if user_data.pic_7:
            #     pic_7 = user_data.pic_8.url
            # else:
            #     pic_7 = ''
            # if user_data.pic_8:
            #     pic_8 = user_data.pic_8.url
            # else:
            #     pic_8 = ''
            # if user_data.pic_9:
            #     pic_9 = user_data.pic_9.url
            # else:
            #     pic_9 = ''
            Data = {
                "id": user_data.id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "phone_number": user_data.phone_number,
                "gender": user_data.gender,
                "date_of_birth": user_data.date_of_birth,
                # "job_profile": user_data.job_profile,
                # "company_name": user_data.company_name,
                # "qualification": user_data.qualification,
                # "relationship_status": user_data.relationship_status,
                # "interests": user_data.interests,
                # "fav_quote": user_data.fav_quote,
                "pic_1": pic_1,
                "pic_2": pic_2,
                "pic_3": pic_3,
                "pic_4": pic_4,
                "pic_5": pic_5,
                "pic_6": pic_6,
                # "pic_7": pic_7,
                # "pic_8": pic_8,
                # "pic_9": pic_9,
                "discovery_lat": user_detail.discovery[0],
                "discovery_lang": user_detail.discovery[1],
                "distance_range": user_detail.distance_range,
                "min_age_range": user_detail.min_age_range,
                "max_age_range": user_detail.max_age_range,
                "interested": user_detail.interest
            }
            token = Token.objects.get_or_create(user=us_obj)
            return Response(
                {"message": "User Created successfully", "Data": Data, 'token': token[0].key, "status": HTTP_200_OK})
        else:
            return Response({"message": serializer.errors, "status": HTTP_400_BAD_REQUEST})


class UpdatePhoneNumber(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.phone_number = request.data.get('phone_number')
        user.save()
        user_obj.phone_number = request.data.get('phone_number')
        user_obj.save()
        UserNotification.objects.create(
            to=user,
            title='Mobile Number Update',
            body='Your mobile number has been updated successfully',
        )
        return Response({"message": "Your phone number has been updated", "status": HTTP_200_OK})


class UpdateEmail(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.email = request.data.get('email')
        user.save()
        user_obj.email = request.data.get('email')
        user_obj.save()
        UserNotification.objects.create(
            to=user,
            title='Email Update',
            body='Your email has been updated successfully',
        )
        return Response({"message": "Your email has been updated", "status": HTTP_200_OK})


class UpdateProfilePic(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_1 = request.data.get('pic_1')
        user.save()
        user_obj.pic_1 = request.data.get('pic_1')
        user_obj.save()
        UserNotification.objects.create(
            to=user,
            title='Profile pic Update',
            body='Your profile pic been updated successfully',
        )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class UpdateProfilePic_1(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_1 = request.data.get('pic_1')
        user.save()
        user_obj.pic_1 = request.data.get('pic_1')
        user_obj.save()
        # UserNotification.objects.create(
        #     to=user,
        #     title='Profile pic Update',
        #     body='Your profile pic been updated successfully',
        # )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class UpdateProfilePic_2(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_2 = request.data.get('pic_2')
        user.save()
        user_obj.pic_2 = request.data.get('pic_2')
        user_obj.save()
        # UserNotification.objects.create(
        #     to=user,
        #     title='Profile pic Update',
        #     body='Your profile pic been updated successfully',
        # )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class UpdateProfilePic_3(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_3 = request.data.get('pic_3')
        user.save()
        user_obj.pic_3 = request.data.get('pic_3')
        user_obj.save()
        # UserNotification.objects.create(
        #     to=user,
        #     title='Profile pic Update',
        #     body='Your profile pic been updated successfully',
        # )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class UpdateProfilePic_4(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_4 = request.data.get('pic_4')
        user.save()
        user_obj.pic_4 = request.data.get('pic_4')
        user_obj.save()
        # UserNotification.objects.create(
        #     to=user,
        #     title='Profile pic Update',
        #     body='Your profile pic been updated successfully',
        # )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class UpdateProfilePic_5(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_5 = request.data.get('pic_5')
        user.save()
        user_obj.pic_5 = request.data.get('pic_5')
        user_obj.save()
        # UserNotification.objects.create(
        #     to=user,
        #     title='Profile pic Update',
        #     body='Your profile pic been updated successfully',
        # )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class UpdateProfilePic_6(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        print(self.request.data)
        print(self.request.META)
        user = self.request.user
        print(user)
        # instance = self.get_object()
        # instance.phone_number = request.data.get('phone_number')
        # instance.save(update_fields=['phone_number'])
        user_obj = RegisterUser.objects.get(email=user.email)
        user.pic_6 = request.data.get('pic_6')
        user.save()
        user_obj.pic_6 = request.data.get('pic_6')
        user_obj.save()
        # UserNotification.objects.create(
        #     to=user,
        #     title='Profile pic Update',
        #     body='Your profile pic been updated successfully',
        # )
        return Response({"message": "Your profile pic has been updated", "status": HTTP_200_OK})


class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.device_token = ''
        user.save()
        request.user.auth_token.delete()
        return Response({"msg": "Logged out successfully", "status": HTTP_200_OK})


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileAPIView(ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        # id = self.request.GET.get('id')
        try:
            logged_in_user = self.request.user
            print(logged_in_user)
            print(logged_in_user.phone_number)
            register_id = RegisterUser.objects.get(email=logged_in_user.email)
            print(register_id)
            user = UserDetail.objects.get(phone_number=register_id)
            print(user)
            r_user = RegisterUser.objects.get(email=logged_in_user.email)
            account = DeactivateAccount.objects.get(user=r_user)
            pic_1 = ''
            pic_2 = ''
            pic_3 = ''
            pic_4 = ''
            pic_5 = ''
            pic_6 = ''
            # pic_7 = ''
            # pic_8 = ''
            # pic_9 = ''
            if user.phone_number.pic_1:
                pic_1 = user.phone_number.pic_1.url
            else:
                pic_1 = ''
            if user.phone_number.pic_2:
                pic_2 = user.phone_number.pic_2.url
            else:
                pic_2 = ''
            if user.phone_number.pic_3:
                pic_3 = user.phone_number.pic_3.url
            else:
                pic_3 = ''
            if user.phone_number.pic_4:
                pic_4 = user.phone_number.pic_4.url
            else:
                pic_4 = ''
            if user.phone_number.pic_5:
                pic_5 = user.phone_number.pic_5.url
            else:
                pic_5 = ''
            if user.phone_number.pic_6:
                pic_6 = user.phone_number.pic_6.url
            else:
                pic_6 = ''
            # if user.phone_number.pic_7:
            #     pic_7 = user.phone_number.pic_7.url
            # else:
            #     pic_7 = ''
            # if user.phone_number.pic_8:
            #     pic_8 = user.phone_number.pic_8.url
            # else:
            #     pic_8 = ''
            # if user.phone_number.pic_9:
            #     pic_9 = user.phone_number.pic_9.url
            # else:
            #     pic_9 = ''
            detail = {
                "id": user.phone_number.id,
                "bio": user.bio,
                "address": user.address,
                "hashtag": user.phone_number.hashtag,
                "first_name": user.phone_number.first_name,
                "last_name": user.phone_number.last_name,
                "email": user.phone_number.email,
                "gender": user.phone_number.gender,
                "date_of_birth": user.phone_number.date_of_birth,
                "job_profile": user.phone_number.job_profile,
                "company_name": user.phone_number.company_name,
                "qualification": user.phone_number.qualification,
                "relationship_status": user.phone_number.relationship_status,
                "height": user.phone_number.height,
                "zodiac_sign": user.phone_number.zodiac_sign,
                "fav_quote": user.phone_number.fav_quote,
                "religion": user.phone_number.religion,
                "body_type": user.phone_number.body_type,
                "verified": user.phone_number.verified,
                "fb_signup": user.phone_number.fb_signup,
                "pic_1": pic_1,
                "pic_2": pic_2,
                "pic_3": pic_3,
                "pic_4": pic_4,
                "pic_5": pic_5,
                "pic_6": pic_6,
                # "pic_7": pic_7,
                # "pic_8": pic_8,
                # "pic_9": pic_9,
                "living_in": user.living_in,
                "hometown": user.hometown,
                "profession": user.profession,
                "college_name": user.college_name,
                "university": user.university,
                "personality": user.personality,
                "preference_first_date": user.preference_first_date,
                "fav_music": user.fav_music,
                "interest": user.interest,
                "food_type": user.food_type,
                "owns": user.owns,
                "travelled_place": user.travelled_place,
                "once_in_life": user.once_in_life,
                "exercise": user.exercise,
                "looking_for": user.looking_for,
                "fav_food": user.fav_food,
                "fav_pet": user.fav_pet,
                "smoke": user.smoke,
                "drink": user.drink,
                "subscription_purchased": user.subscription_purchased,
                "subscription_purchased_at": user.subscription_purchased_at,
                "discovery_lat": user.discovery[0],
                "discovery_lang": user.discovery[1],
                "distance_range": user.distance_range,
                "min_age_range": user.min_age_range,
                "max_age_range": user.max_age_range,
                "deactivated": account.deactivated
            }
            return Response({"data": detail, "status": HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], "status": HTTP_400_BAD_REQUEST})


class UserProfileUpdateView(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDetailSerializer
    queryset = UserDetail.objects.all()

    def update(self, request, *args, **kwargs):
        user = self.request.user
        print(user)
        print(self.request.data)
        register_id = RegisterUser.objects.get(email=user.email)
        # register_id.date_of_birth = request.data.get("date_of_birth")
        register_id.qualification = request.data.get("qualification")
        register_id.religion = request.data.get("religion")
        register_id.body_type = request.data.get("body_type")
        register_id.relationship_status = request.data.get("relationship_status")
        register_id.fav_quote = request.data.get("fav_quote")
        register_id.height = request.data.get("height")
        register_id.hashtag = request.data.get("hashtag")
        register_id.zodiac_sign = request.data.get("zodiac_sign")
        register_id.save(
            update_fields=['qualification', 'religion', 'body_type', 'relationship_status',
                           'fav_quote', 'height', 'zodiac_sign', 'hashtag'])
        # print(register_id.pic_1)
        # print(register_id.pic_2)
        # print(register_id.pic_3)
        # print(register_id.pic_4)
        # print(register_id.pic_5)
        # print(register_id.pic_6)
        userdetail_obj = UserDetail.objects.get(phone_number=register_id)
        # instance = self.get_object()
        userdetail_obj.bio = request.data.get("bio")
        userdetail_obj.living_in = request.data.get("living_in")
        userdetail_obj.hometown = request.data.get("hometown")
        userdetail_obj.profession = request.data.get("profession")
        userdetail_obj.college_name = request.data.get("college_name")
        userdetail_obj.university = request.data.get("university")
        userdetail_obj.personality = request.data.get("personality")
        userdetail_obj.preference_first_date = request.data.get("preference_first_date")
        userdetail_obj.fav_music = request.data.get("fav_music")
        userdetail_obj.food_type = request.data.get("food_type")
        userdetail_obj.owns = request.data.get("owns")
        userdetail_obj.travelled_place = request.data.get("travelled_place")
        userdetail_obj.once_in_life = request.data.get("once_in_life")
        userdetail_obj.exercise = request.data.get("exercise")
        userdetail_obj.looking_for = request.data.get("looking_for")
        userdetail_obj.fav_food = request.data.get("fav_food")
        userdetail_obj.fav_pet = request.data.get("fav_pet")
        userdetail_obj.smoke = request.data.get("smoke")
        userdetail_obj.drink = request.data.get("drink")
        userdetail_obj.interest = request.data.get("interest")
        # userdetail_obj.height = request.data.get("height")
        # instance.subscription_purchased = request.data.get(
        #     "subscription_purchased")
        # instance.subscription_purchased_at = request.data.get(
        #     "subscription_purchased_at")
        # id = request.data.get("subscription")
        # id = int(id)
        # subscription = SubscriptionPlans.objects.get(id=id)
        # instance.subscription = subscription
        userdetail_obj.save(
            update_fields=['bio', 'phone_number', 'living_in', 'hometown', 'profession', 'college_name',
                           'university',
                           'personality', 'preference_first_date', 'fav_music', 'travelled_place',
                           'once_in_life', 'exercise', 'looking_for', 'fav_food', 'owns', 'food_type', 'fav_pet',
                           'smoke', 'drink', 'interest'])
        # from_id = User.objects.filter(is_superuser=True)[0].id
        # from_user_id = RegisterUser.objects.get(id=from_id)
        # from_user_name = from_user_id.first_name
        # phone_number = self.request.data['phone_number']
        # to_user = RegisterUser.objects.get(id=phone_number)
        # first_name = to_user.first_name
        # to_id = self.request.data['phone_number']
        # to_user_id = RegisterUser.objects.get(id=to_id)
        # UserNotification.objects.create(
        #     from_user_id=from_user_id,
        #     from_user_name=from_user_name,
        #     to_user_id=to_user_id,
        #     to_user_name=first_name,
        #     notification_type="Profile Update",
        #     notification_title="Profile Update",
        #     notification_body="Your profile has been updated"
        # )

        return Response({"message": "Profile updated successfully", "status": HTTP_200_OK})


class GetUserInstagramPics(APIView):
    serializer_class = GetInstagramPicSerializer

    def post(self, request, *args, **kwargs):
        username = self.request.data['username']
        password = self.request.data['password']
        loader = instaloader.Instaloader()
        USERNAME = username
        PASSWORD = password
        DOWNLOADED_POST_DIRECTORY = "Fetched_Posts"
        try:
            loader.login(USERNAME, PASSWORD)
        except Exception as e:
            x = {"Error": str(e)}
            return Response(x["Error"], status=HTTP_400_BAD_REQUEST)
        posts_array = instaloader.Profile.from_username(
            loader.context, USERNAME).get_posts()
        count = 0
        images = []
        number_of_posts = 0
        for post in posts_array:
            loader.download_post(post, DOWNLOADED_POST_DIRECTORY)
            number_of_posts += 1
            if number_of_posts == 10:
                break
        for f in os.listdir('./Fetched_Posts'):
            if f.endswith('.jpg'):
                while count < 10:
                    images.append(f)
                    count += 1
                    break
        if os.path.isdir("Fetched_Posts"):
            shutil.rmtree("Fetched_Posts")
            print("Deleted folder {} successfully".format("Fetched_Posts"))
        return Response({"Success": "Downloaded images from instagram successfully", "Images": images},
                        status=HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class UserInstagramPicsAPIView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserInstagramSerializer

    def post(self, request, *args, **kwargs):
        # phone_number = self.request.data['id']
        user = self.request.user
        p_no = RegisterUser.objects.get(email=user.email)
        insta_pic_0 = self.request.data['insta_pic_0']
        insta_pic_1 = self.request.data['insta_pic_1']
        insta_pic_2 = self.request.data['insta_pic_2']
        insta_pic_3 = self.request.data['insta_pic_3']
        insta_pic_4 = self.request.data['insta_pic_4']
        insta_pic_5 = self.request.data['insta_pic_5']
        insta_pic_6 = self.request.data['insta_pic_6']
        insta_pic_7 = self.request.data['insta_pic_7']
        insta_pic_8 = self.request.data['insta_pic_8']
        insta_pic_9 = self.request.data['insta_pic_9']
        UserInstagramPic.objects.create(
            phone_number=p_no,
            insta_pic_1=insta_pic_0,
            insta_pic_2=insta_pic_1,
            insta_pic_3=insta_pic_2,
            insta_pic_4=insta_pic_3,
            insta_pic_5=insta_pic_4,
            insta_pic_6=insta_pic_5,
            insta_pic_7=insta_pic_6,
            insta_pic_8=insta_pic_7,
            insta_pic_9=insta_pic_8,
            insta_pic_10=insta_pic_9,
            insta_connect=True
        )
        p_no.verified = True
        p_no.save()
        return Response({"Success": "Images uploaded from instagram successfully", "status": HTTP_200_OK})


class UpdateVerifiedStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = RegisterUser

    def post(self, request, *args, **kwargs):
        user = self.request.user
        p_no = RegisterUser.objects.get(email=user.email)
        p_no.verified = True
        p_no.save()
        return Response({"message": 'Verified successfully', 'status': HTTP_200_OK})


class GetVerifiedStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = RegisterUser

    def get(self, request, *args, **kwargs):
        user = self.request.user
        p_no = RegisterUser.objects.get(email=user.email)
        # p_no.verified = True
        # p_no.save()
        return Response(
            {"message": 'Verified status fetched successfully', 'verified': p_no.verified, 'status': HTTP_200_OK})


class ShowInstagramPics(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShowInstaPics

    def get(self, request, *args, **kwargs):
        id = self.request.GET.get('user_id')
        user = self.request.user
        r_user = RegisterUser.objects.get(id=id)
        try:
            pics = UserInstagramPic.objects.filter(phone_number=r_user).last()
            print(pics)
            # print(len(pics))
            pics_list = []
            if pics:
                insta_pic_1 = pics.insta_pic_1
                insta_pic_2 = pics.insta_pic_2
                insta_pic_3 = pics.insta_pic_3
                insta_pic_4 = pics.insta_pic_4
                insta_pic_5 = pics.insta_pic_5
                insta_pic_6 = pics.insta_pic_6
                insta_pic_7 = pics.insta_pic_7
                insta_pic_8 = pics.insta_pic_8
                insta_pic_9 = pics.insta_pic_9
                insta_pic_10 = pics.insta_pic_10
                pics_data = {
                    "insta_pic_1": insta_pic_1,
                    "insta_pic_2": insta_pic_2,
                    "insta_pic_3": insta_pic_3,
                    "insta_pic_4": insta_pic_4,
                    "insta_pic_5": insta_pic_5,
                    "insta_pic_6": insta_pic_6,
                    "insta_pic_7": insta_pic_7,
                    "insta_pic_8": insta_pic_8,
                    "insta_pic_9": insta_pic_9,
                    "insta_pic_10": insta_pic_10,
                    'insta_verified': pics.insta_connect
                }
                return Response({"pics": pics_data, 'status': HTTP_200_OK})
            else:
                pics_data = {
                    "insta_pic_1": '',
                    "insta_pic_2": '',
                    "insta_pic_3": '',
                    "insta_pic_4": '',
                    "insta_pic_5": '',
                    "insta_pic_6": '',
                    "insta_pic_7": '',
                    "insta_pic_8": '',
                    "insta_pic_9": '',
                    "insta_pic_10": '',
                    'insta_verified': False
                }
                return Response({'pics': pics_data, 'status': HTTP_200_OK})
        except Exception as e:
            print(e)
            x = {'error': str(e)}
            return Response({"message": x['error'], 'status': HTTP_400_BAD_REQUEST})


class UserslistAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        # queryset needed to be filtered
        # logged_in_user_id = self.request.GET.get('id')
        logged_in_user_id = self.request.user
        # print('Logged in user email ', logged_in_user_id.email)
        registr_user = RegisterUser.objects.get(email=logged_in_user_id.email)
        # print('Register user instance email ', registr_user.email)
        #
        # print('Email after excluding logged in user ',
        #       [x.phone_number.email for x in UserDetail.objects.all().exclude(phone_number=registr_user.id)])
        # print('All users email ', [x.phone_number.email for x in UserDetail.objects.all()])
        # print([x.id for x in UserDetail.objects.all()])
        # print([UserDetail.objects.get(id=registr_user.id).phone_number.email])
        # user = UserDetail.objects.get(phone_number=registr_user)
        # queryset1 = RegisterUser.objects.all().exclude(id=logged_in_user_id).values()
        users = []
        # for obj in queryset1:
        #     users.append(obj)
        # return Response({"Users":users}, HTTP_200_OK)
        user_detail_obj = UserDetail.objects.get(phone_number=registr_user.id)
        lang = user_detail_obj.discovery[0]
        lat = user_detail_obj.discovery[1]
        distance_range = user_detail_obj.distance_range
        if distance_range and user_detail_obj.max_age_range and user_detail_obj.min_age_range:
            users_location = fromstr('Point({} {})'.format(lat, lang), srid=4326)
            users_in_range = UserDetail.objects.filter(
                discovery__distance_lte=(users_location, D(km=distance_range))).exclude(
                phone_number=registr_user.id).exclude(phone_number=registr_user.id)
            # print(users_in_range.filter(min_age_range__gte=obj.phone_number.get_user_age(),max_age_range__lte=))
            print('>>>>>>>>>>>>>>>> Filtered Users -->', users_in_range)
            f_u = []
            for u in users_in_range:
                if u.min_age_range <= u.phone_number.get_user_age() <= u.max_age_range:
                    f_u.append(u)
                else:
                    pass
            print(' From if case Filtered users---------------', f_u)
        else:
            users_location = fromstr('Point({} {})'.format(lat, lang), srid=4326)
            users_in_range = UserDetail.objects.filter(
                discovery__distance_lte=(users_location, D(km=2))).exclude(
                phone_number=registr_user.id).exclude(phone_number=registr_user.id)
            print('Else case Filtered users---------------', users_in_range)
        # print('>>>>>>>>>>>>>>>> Age  -->', )
        if (UserDetail.objects.all().exclude(phone_number=registr_user.id)).count() > 0:
            for obj in (UserDetail.objects.all().exclude(phone_number=registr_user.id)):
                print('>>>>>>>>>>>>>>>> Age  -->', obj.phone_number.get_user_age())
                # print('>>>>>>>>>>>>>>>> Age  -->', obj.phone_number.get_user_age)
                id = obj.id
                bio = obj.bio
                first_name = obj.phone_number.first_name
                last_name = obj.phone_number.last_name
                email = obj.phone_number.email
                gender = obj.phone_number.gender
                date_of_birth = obj.phone_number.date_of_birth
                job_profile = obj.phone_number.job_profile
                company_name = obj.phone_number.company_name
                qualification = obj.phone_number.qualification
                relationship_status = obj.phone_number.relationship_status
                height = obj.phone_number.height
                fav_quote = obj.phone_number.fav_quote
                religion = obj.phone_number.religion
                body_type = obj.phone_number.body_type
                verified = obj.phone_number.verified
                fb_signup = obj.phone_number.fb_signup
                pic_1 = ''
                pic_2 = ''
                pic_3 = ''
                pic_4 = ''
                pic_5 = ''
                pic_6 = ''
                if obj.phone_number.pic_1:
                    pic_1 = obj.phone_number.pic_1.url
                else:
                    pic_1 = ''
                if obj.phone_number.pic_2:
                    pic_2 = obj.phone_number.pic_2.url
                else:
                    pic_2 = ''
                if obj.phone_number.pic_3:
                    pic_3 = obj.phone_number.pic_3.url
                else:
                    pic_3 = ''
                if obj.phone_number.pic_4:
                    pic_4 = obj.phone_number.pic_4.url
                else:
                    pic_4 = ''
                if obj.phone_number.pic_5:
                    pic_5 = obj.phone_number.pic_5.url
                else:
                    pic_5 = ''
                if obj.phone_number.pic_6:
                    pic_6 = obj.phone_number.pic_6.url
                else:
                    pic_6 = ''
                # if obj.phone_number.pic_7:
                #     pic_7 = obj.phone_number.pic_7.url
                # else:
                #     pic_7 = ''
                # if obj.phone_number.pic_8:
                #     pic_8 = obj.phone_number.pic_8.url
                # else:
                #     pic_8 = ''
                # if obj.phone_number.pic_9:
                #     pic_9 = obj.phone_number.pic_9.url
                # else:
                #     pic_9 = ''
                living_in = obj.living_in
                hometown = obj.hometown
                profession = obj.profession
                college_name = obj.college_name
                university = obj.university
                personality = obj.personality
                preference_first_date = obj.preference_first_date
                fav_music = obj.fav_music
                travelled_place = obj.travelled_place
                once_in_life = obj.once_in_life
                exercise = obj.exercise
                looking_for = obj.looking_for
                fav_food = obj.fav_food
                interest = obj.interest
                fav_pet = obj.fav_pet
                smoke = obj.smoke
                drink = obj.drink
                subscription_purchased = obj.subscription_purchased
                subscription_purchased_at = obj.subscription_purchased_at
                # subscription = obj.subscription.values()
                detail = {
                    "id": id,
                    "bio": bio,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "gender": gender,
                    "date_of_birth": date_of_birth,
                    "job_profile": job_profile,
                    "company_name": company_name,
                    "qualification": qualification,
                    "relationship_status": relationship_status,
                    "height": height,
                    "fav_quote": fav_quote,
                    "religion": religion,
                    "body_type": body_type,
                    "verified": verified,
                    "fb_signup": fb_signup,
                    "pic_1": pic_1,
                    "pic_2": pic_2,
                    "pic_3": pic_3,
                    "pic_4": pic_4,
                    "pic_5": pic_5,
                    "pic_6": pic_6,
                    # "pic_7": pic_7,
                    # "pic_8": pic_8,
                    # "pic_9": pic_9,
                    "living_in": living_in,
                    "hometown": hometown,
                    "profession": profession,
                    "college_name": college_name,
                    "university": university,
                    "personality": personality,
                    "preference_first_date": preference_first_date,
                    "fav_music": fav_music,
                    "travelled_place": travelled_place,
                    "once_in_life": once_in_life,
                    "exercise": exercise,
                    "looking_for": looking_for,
                    "fav_food": fav_food,
                    "interest": interest,
                    "fav_pet": fav_pet,
                    "smoke": smoke,
                    "drink": drink,
                    "subscription_purchased": subscription_purchased,
                    "subscription_purchased_at": subscription_purchased_at,
                    # "subscription": subscription
                }
                users.append(detail)
            return Response({"data": users, "status": HTTP_200_OK})
        else:
            return Response({"message": "No users found", "status": HTTP_200_OK})


class FilteredUserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserDetail
    serializer_class = UserDetailSerializer

    def post(self, request, *args, **kwargs):
        logged_in_user_id = self.request.user
        register_user = RegisterUser.objects.get(email=logged_in_user_id.email)
        print(register_user.id)
        user_detail_obj = UserDetail.objects.get(phone_number=register_user.id)
        users_blocked_by_me = BlockedUsers.objects.filter(user=register_user)
        print('USERS BLOCKED BY ME ', users_blocked_by_me)
        # users_blocked_by_me_list_2 = [x for x in users_blocked_by_me for y in x.blocked.all()]
        # print('BLOCKED LIST 2', users_blocked_by_me_list_2)

        ### latest setting change
        show_only_liked_profiles_list = []
        users_liked_by_show_only_liked_profiles = []
        users_details_liked_by_show_only_liked_profiles = []
        show_only_liked_profiles_obj = RegisterUser.objects.filter(show_only_to_liked=True)
        for user in show_only_liked_profiles_obj:
            liked_by_me = MatchedUser.objects.filter(user=user)
            if register_user in liked_by_me.all():
                users_liked_by_show_only_liked_profiles.append(user)
        for user in users_details_liked_by_show_only_liked_profiles:
            users_details_liked_by_show_only_liked_profiles.append(UserDetail.objects.get(phone_number=user))
        # for user in show_only_liked_profiles_obj:
        #     show_only_liked_profiles_list.append(user)
        # for user in show_only_liked_profiles_list:
        #     users_liked_by_show_only_liked_profiles.append(MatchedUser.objects.filter(user=user))
        ### End latest setting block
        users_blocked_by_me_list = []
        for user in users_blocked_by_me:
            for u in user.blocked.all():
                users_blocked_by_me_list.append(u.id)
        print('USERS BLOCKED BY ME LIST---', users_blocked_by_me_list)
        users_blocked_me = BlockedUsers.objects.filter(blocked=register_user)
        print('USERS BLOCKED ME ID', [x.user.id for x in users_blocked_me])
        # users_blocked_me_list = [x.id for x in users_blocked_me.blocked.all()]
        users_blocked_me_list = []
        for user in users_blocked_me:
            users_blocked_me_list.append(user.user.id)
        print('USERS BLOCKED ME ', users_blocked_me_list)
        final_blocked_users_list = users_blocked_by_me_list + users_blocked_me_list
        print('FINAL BLOCKED LIST', final_blocked_users_list)
        lang = 0
        lat = 0
        if user_detail_obj.discovery:
            lang = user_detail_obj.discovery[0]
        if user_detail_obj.discovery:
            lat = user_detail_obj.discovery[1]
        if user_detail_obj.distance_range:
            distance_range = user_detail_obj.distance_range
        distance_range = user_detail_obj.distance_range
        print(distance_range)
        max_age_range = user_detail_obj.max_age_range
        min_age_range = user_detail_obj.min_age_range
        print('MIN AND MAX AGE RANGE---- ', min_age_range, max_age_range)
        liked_users = MatchedUser.objects.filter(user=register_user).distinct()
        disliked_users = MatchedUser.objects.filter(user=register_user).distinct()
        print('Liked Users---->>', liked_users)
        print('Disliked users----->>', disliked_users)
        l = []
        for x in liked_users:
            for y in x.liked_by_me.all():
                l.append(y.id)
        for y in liked_users:
            for z in y.super_liked_by_me.all():
                l.append(z)
        print(l)
        d = []
        for x in disliked_users:
            for y in x.disliked_by_me.all():
                d.append(y.id)
        print('Disliked ', d)
        print('Liked Disliked list ', l + d)
        liked_disliked_user_detail = []
        for x in l + d:
            if x in liked_disliked_user_detail:
                pass
            else:
                liked_disliked_user_detail.append(UserDetail.objects.get(phone_number=x))
        f_u = []
        print('Lang and Lat', lang, lat)
        print('LIKED DISLIKED USER DETAIL--->>', liked_disliked_user_detail)
        users_location = fromstr('Point({} {})'.format(lang, lat), srid=4326)
        # users_in_range = UserDetail.objects.filter(
        #     discovery__distance_lte=(users_location, D(km=distance_range))).exclude(
        #     phone_number=register_user.id).exclude(phone_number=register_user.id)
        # users_in_range = UserDetail.objects.annotate(
        #     discovery__distance=GeometryDistance("discovery__distance", users_location)).filter(
        #     discovery__distance_lte=(int(distance_range)) * 1000)

        #### TESTING PURPOSRE
        # Point(x, y)
        #
        # x = longitude
        #
        # y = latitude
        # from django.contrib.gis.geos import Point
        # xyz = (int(distance_range))
        # point = Point(lang, lat)
        # x = UserDetail.objects.filter(discovery__distance_lte=(point, Distance(km=xyz))).exclude(
        #     phone_number=register_user.id).order_by(
        #     "id").exclude(deactivated=True)
        # y = UserDetail.objects.filter(discovery__distance_lte=(point, D(km=xyz))).exclude(
        #     phone_number=register_user.id).order_by(
        #     "id").exclude(deactivated=True)
        # z = UserDetail.objects.filter(discovery__distance_dwithin=(point, D(km=xyz))).exclude(
        #     phone_number=register_user.id).order_by(
        #     "id").exclude(deactivated=True)
        # print('<<<<<<<<<<-------------ZZZZZZZZZZZZZZ----------->>>>>>>', z)
        # print('<<<<<<<<<<-------------YYYYYYYYYYYYYY----------->>>>>>>', y)
        # print('<<<-----XXXXXXXXXXXXXXXXXXXXXXXXXX------>>>>>>', x)
        # print('LOGGED IN USER ID', UserDetail.objects.get(phone_number=register_user.id).id)
        # print('USER DETAIL 46', UserDetail.objects.get(id=46).discovery[0], UserDetail.objects.get(id=46).discovery[1])
        # print('USER DETAIL 47', UserDetail.objects.get(id=47).discovery[0], UserDetail.objects.get(id=47).discovery[1])
        # print('USER DETAIL 44', UserDetail.objects.get(id=44).discovery[0], UserDetail.objects.get(id=44).discovery[1])
        # users_in_range = UserDetail.objects.filter(
        #     discovery__dwithin=(users_location, (int(distance_range) * 1000))).annotate(
        #     distance=GeometryDistance("discovery", users_location)).exclude(phone_number=register_user.id).order_by(
        #     "distance").exclude(deactivated=True)
        # print('--------------------------', [x.id for x in users_in_range])
        # from django.contrib.gis.geos import Point
        # p1 = Point(UserDetail.objects.get(id=46).discovery[0], UserDetail.objects.get(id=46).discovery[1])
        # p2 = Point(UserDetail.objects.get(id=47).discovery[0], UserDetail.objects.get(id=47).discovery[1])
        # p3 = Point(UserDetail.objects.get(id=44).discovery[0], UserDetail.objects.get(id=44).discovery[1])
        # # distance = p1.distance(p2)
        # distance = p1.distance(p3)
        # distance_in_km = distance * 100
        # print('DISTANCE BETWEEN USER 46 , 47', distance_in_km)
        #### END TESTING PURPOSE

        d = (int(distance_range) * 1000)
        users_in_range = UserDetail.objects.filter(discovery__dwithin=(users_location, d)).annotate(
            distance=GeometryDistance("discovery", users_location)).exclude(phone_number=register_user.id).order_by(
            "distance").exclude(deactivated=True)
        # print(users_in_range.filter(min_age_range__gte=obj.phone_number.get_user_age(),max_age_range__lte=))
        print('>>>>>>>>>>>>>>>> Filtered Users -->', users_in_range)
        print('-----------------------------', len(liked_disliked_user_detail))
        list_after_liked_disliked = []
        if len(users_in_range) > 0:
            if len(set(liked_disliked_user_detail)) > 0:
                for y in users_in_range:
                    if y in [x for x in set(liked_disliked_user_detail)]:
                        pass
                    else:
                        if y.phone_number.show_only_to_liked:
                            if y in users_details_liked_by_show_only_liked_profiles:
                                list_after_liked_disliked.append(y)
                            else:
                                pass
                        else:
                            list_after_liked_disliked.append(y)
            else:
                for y in users_in_range:
                    list_after_liked_disliked.append(y)
        else:
            pass
        print('LIST AFTER LIKED AND DISLIKED REMOVAL---', list_after_liked_disliked)
        for u in set(list_after_liked_disliked):
            if min_age_range <= u.phone_number.get_user_age() <= max_age_range:
                f_u.append(u)
            else:
                pass
        print(' From if case Filtered users---------------', f_u)
        incoming_filter_query_list = []
        user_detail_incoming_filter = []
        or_filtered_data_list = []
        qualification = self.request.POST.get('qualification' or None)
        relationship_status = self.request.POST.get('relationship_status' or None)
        religion = self.request.POST.get('religion' or None)
        body_type = self.request.POST.get('body_type' or None)
        gender = self.request.POST.get('gender' or None)
        height = self.request.POST.get('height' or None)
        zodiac_sign = self.request.POST.get('zodiac_sign' or None)
        taste = self.request.POST.get('taste' or None)
        verified = self.request.POST.get('verified' or None)
        smoke = self.request.POST.get('smoke' or None)
        drink = self.request.POST.get('drink' or None)
        # print('qualification--->>>', qualification)
        # print('relationship_status---->>', relationship_status)
        # print('religion---->>', religion)
        # print('body_type--->>', body_type)
        # print('gender--->>>', gender)
        # print('height--->>>', height)
        # print('zodiac_sign--->>', zodiac_sign)
        # print('taste____>>>', taste)
        if smoke:
            print('INSIDE SMOKE---->>>', smoke)
            user_detail_incoming_filter.append({'smoke': smoke})
        if drink:
            print('INSIDE DRINK---->>>', drink)
            user_detail_incoming_filter.append({'drink': drink})
        if qualification:
            incoming_filter_query_list.append({'qualification': qualification})
        if verified:
            incoming_filter_query_list.append({'verified': verified})
        if relationship_status:
            incoming_filter_query_list.append({'relationship_status': relationship_status})
        if religion:
            incoming_filter_query_list.append({'religion': religion})
        if body_type:
            incoming_filter_query_list.append({'body_type': body_type})
        if gender:
            incoming_filter_query_list.append({'gender': gender})
        if height:
            incoming_filter_query_list.append({'height': height})
        if zodiac_sign:
            incoming_filter_query_list.append({'zodiac_sign': zodiac_sign})
        if taste:
            incoming_filter_query_list.append({'taste': taste})
        for value in incoming_filter_query_list:
            r = RegisterUser.objects.filter(**value)
            if r:
                for x in r:
                    print('__________________________XXXXXXXXXXXXX', x)
                    if x:
                        if x in or_filtered_data_list:
                            pass
                        else:
                            print('FROM FILTER', x == register_user)
                            if x == register_user:
                                pass
                            else:
                                or_filtered_data_list.append(x)
                    else:
                        pass
            else:
                pass
        for value in user_detail_incoming_filter:
            user_detail = UserDetail.objects.filter(**value)
            print(UserDetail.objects.filter(smoke='No'))
            print('INSIDE SMOKE AND DRINK FILTER---->>>', user_detail)
            if user_detail:
                for y in user_detail:
                    print('YYYYYYYYYYYYY______', y)
                    print('YYYYYYYYYYYYYYY PHONE NUMBER', y.phone_number)
                    print('Y PHONENUMBER ID----', y.phone_number.id)
                    if y:
                        print(RegisterUser.objects.get(id=y.phone_number.id))
                        if RegisterUser.objects.get(id=y.phone_number.id) in or_filtered_data_list:
                            pass
                        else:
                            print('>>>>>>>>>>>>>>>>>>>',
                                  RegisterUser.objects.get(id=y.phone_number.id) == register_user)
                            if RegisterUser.objects.get(id=y.phone_number.id) == register_user:
                                pass
                            else:
                                or_filtered_data_list.append(RegisterUser.objects.get(id=y.phone_number.id))
                    else:
                        pass
            else:
                pass
        print('LLLLLLLLEEEEEEEEEEEEENN', len(incoming_filter_query_list))
        print('OR FILTERED LIST', or_filtered_data_list)
        # filters = {
        #     key: value
        #     for key, value in self.request.POST.items()
        #     if
        #     key in ['qualification', 'relationship_status', 'religion', 'body_type', 'gender', 'height', 'zodiac_sign',
        #             'taste']
        # }
        # print('FILTERS--------->>>', filters)
        # print('REGISTER USER OBJECTS', RegisterUser.objects.filter(**filters))
        z = []
        for x in f_u:
            print('XXXXXXXXXXXXXX-----------', x)
            print(x.phone_number.email)
            r_u = RegisterUser.objects.get(email=x.phone_number.email)
            if r_u.id in final_blocked_users_list:
                print('REGISTER USER ID', r_u.id)
                pass
            else:
                z.append(r_u)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>zzzzzzzzzzz ', z)
        qs = []
        if len(or_filtered_data_list) > 0:
            for user in or_filtered_data_list:
                qs.append(user)
        else:
            print('>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<inside outer else>>>>>>>>>>>>>>>>')
            # qs = z
            pass
        final_list = []
        print('QS_____________>>>>>>>>>>', qs)
        if (incoming_filter_query_list or user_detail_incoming_filter) and len(qs) > 0:
            for y in qs:
                print('between qs and final list', y)
                a = UserDetail.objects.get(phone_number=y.id)
                final_list.append(a)
        elif incoming_filter_query_list or user_detail_incoming_filter:
            print('<<<<<<_______inside elif------>>>')
            final_list = []
        else:
            for x in z:
                if x:
                    y = UserDetail.objects.get(phone_number=x)
                    final_list.append(y)
                else:
                    pass
            print('>>>>>>>>>>>>>>>>>>>>>', final_list)
        print('FINAL LIST ----->>>', final_list)
        filtered_users = []
        for obj in final_list:
            # obj = RegisterUser.objects
            print('inside last loop', obj)
            print('inside last loop register user id', obj.phone_number.id)
            id = obj.phone_number.id
            bio = obj.bio
            first_name = obj.phone_number.first_name
            last_name = obj.phone_number.last_name
            email = obj.phone_number.email
            gender = obj.phone_number.gender
            date_of_birth = obj.phone_number.date_of_birth
            job_profile = obj.phone_number.job_profile
            company_name = obj.phone_number.company_name
            qualification = obj.phone_number.qualification
            relationship_status = obj.phone_number.relationship_status
            height = obj.phone_number.height
            fav_quote = obj.phone_number.fav_quote
            religion = obj.phone_number.religion
            body_type = obj.phone_number.body_type
            verified = obj.phone_number.verified
            fb_signup = obj.phone_number.fb_signup
            pic_1 = ''
            pic_2 = ''
            pic_3 = ''
            pic_4 = ''
            pic_5 = ''
            pic_6 = ''
            if obj.phone_number.pic_1:
                pic_1 = obj.phone_number.pic_1.url
            else:
                pic_1 = ''
            if obj.phone_number.pic_2:
                pic_2 = obj.phone_number.pic_2.url
            else:
                pic_2 = ''
            if obj.phone_number.pic_3:
                pic_3 = obj.phone_number.pic_3.url
            else:
                pic_3 = ''
            if obj.phone_number.pic_4:
                pic_4 = obj.phone_number.pic_4.url
            else:
                pic_4 = ''
            if obj.phone_number.pic_5:
                pic_5 = obj.phone_number.pic_5.url
            else:
                pic_5 = ''
            if obj.phone_number.pic_6:
                pic_6 = obj.phone_number.pic_6.url
            else:
                pic_6 = ''
            # if obj.phone_number.pic_7:
            #     pic_7 = obj.phone_number.pic_7.url
            # else:
            #     pic_7 = ''
            # if obj.phone_number.pic_8:
            #     pic_8 = obj.phone_number.pic_8.url
            # else:
            #     pic_8 = ''
            # if obj.phone_number.pic_9:
            #     pic_9 = obj.phone_number.pic_9.url
            # else:
            #     pic_9 = ''
            living_in = obj.living_in
            hometown = obj.hometown
            profession = obj.profession
            college_name = obj.college_name
            university = obj.university
            personality = obj.personality
            preference_first_date = obj.preference_first_date
            fav_music = obj.fav_music
            travelled_place = obj.travelled_place
            once_in_life = obj.once_in_life
            exercise = obj.exercise
            looking_for = obj.looking_for
            fav_food = obj.fav_food
            interest = obj.interest
            fav_pet = obj.fav_pet
            smoke = obj.smoke
            drink = obj.drink
            subscription_purchased = obj.subscription_purchased
            subscription_purchased_at = obj.subscription_purchased_at
            # subscription = obj.subscription.values()
            detail = {
                "id": id,
                "bio": bio,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "gender": gender,
                "date_of_birth": date_of_birth,
                "job_profile": job_profile,
                "company_name": company_name,
                "qualification": qualification,
                "relationship_status": relationship_status,
                "height": height,
                "fav_quote": fav_quote,
                "owns": obj.owns,
                "religion": religion,
                "body_type": body_type,
                "verified": verified,
                "fb_signup": fb_signup,
                "pic_1": pic_1,
                "pic_2": pic_2,
                "pic_3": pic_3,
                "pic_4": pic_4,
                "pic_5": pic_5,
                "pic_6": pic_6,
                # "pic_7": pic_7,
                # "pic_8": pic_8,
                # "pic_9": pic_9,
                "living_in": living_in,
                "hometown": hometown,
                "profession": profession,
                "college_name": college_name,
                "university": university,
                "personality": personality,
                "preference_first_date": preference_first_date,
                "fav_music": fav_music,
                "travelled_place": travelled_place,
                "once_in_life": once_in_life,
                "exercise": exercise,
                "looking_for": looking_for,
                "fav_food": fav_food,
                "interest": interest,
                "fav_pet": fav_pet,
                "smoke": smoke,
                "drink": drink,
                "subscription_purchased": subscription_purchased,
                "subscription_purchased_at": subscription_purchased_at,
                # "subscription": subscription
            }
            print('after dictionary creation--------------------------------------')
            # if self.request.POST.get('qualification' or None) or self.request.POST.get(
            #         'relationship_status' or None) or self.request.POST.get(
            #     'height' or None) or self.request.POST.get('gender' or None) or self.request.POST.get(
            #     'religion' or None) or self.request.POST.get('zodiac_sign' or None) or self.request.POST.get(
            #     'body_type' or None) or self.request.POST.get('taste' or None):
            #     print('filtered users----->>', detail)
            #     print(obj)
            # if self.request.POST.get('qualification' or None) is not None:
            #     if detail['qualification'] is not None and detail['qualification'] != '' and detail[
            #         'qualification'] == self.request.POST.get('qualification' or None):
            #         filtered_users.append(detail)
            #         print('Inside if ', filtered_users)
            # elif self.request.POST.get('relationship_status' or None) is not None:
            #     if detail['relationship_status'] is not None and detail['relationship_status'] != '' and detail[
            #         'relationship_status'] == self.request.POST.get('relationship_status' or None):
            #         filtered_users.append(detail)
            # elif self.request.POST.get('religion' or None) is not None:
            #     if detail['religion'] is not None and detail['religion'] != '' and detail[
            #         'religion'] == self.request.POST.get('religion' or None):
            #         filtered_users.append(detail)
            # elif self.request.POST.get('body_type' or None) is not None:
            #     if detail['body_type'] is not None and detail['body_type'] != '' and detail[
            #         'body_type'] == self.request.POST.get('body_type' or None):
            #         filtered_users.append(detail)
            # elif self.request.POST.get('gender' or None) is not None:
            #     if detail['gender'] is not None and detail['gender'] != '' and detail[
            #         'gender'] == self.request.POST.get('gender' or None):
            #         filtered_users.append(detail)
            # elif self.request.POST.get('height' or None) is not None:
            #     if detail['height'] is not None and detail['height'] != '' and detail[
            #         'height'] == self.request.POST.get('height' or None):
            #         filtered_users.append(detail)
            # elif self.request.POST.get('zodiac_sign' or None) is not None:
            #     if detail['zodiac_sign'] is not None and detail['zodiac_sign'] != '' and detail[
            #         'zodiac_sign'] == self.request.POST.get('zodiac_sign' or None):
            #         filtered_users.append(detail)
            # elif self.request.POST.get('taste' or None) is not None:
            #     if detail['taste'] is not None and detail['taste'] != '' and detail[
            #         'taste'] == self.request.POST.get('taste' or None):
            #         filtered_users.append(detail)
            # else:
            print('inside else case')
            if user_detail_obj.interest:
                if obj.phone_number.gender == user_detail_obj.interest:
                    print('TRUE FALSE ', obj.phone_number.gender == user_detail_obj.interest)
                    print('OBJ PHONE NUMBER GENDER ', obj.phone_number.gender)
                    print('USER DETAIL OBJ ', user_detail_obj.interest)
                    print('inner if')
                    filtered_users.append(detail)
                else:
                    print('inside nested else case')
                    pass
            else:
                print('outer else')
                filtered_users.append(detail)
        print('FILTERED USERS LIST------------->>>>>>>', filtered_users)
        return Response({'data': filtered_users, 'status': HTTP_200_OK})


class UserDetailAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        phone_number = self.request.GET.get('id')
        print(phone_number)
        # queryset = UserDetail.objects.filter(id=phone_number).values()
        # queryset = UserDetail.objects.filter(id=phone_number)
        register_id = RegisterUser.objects.get(id=phone_number)
        print(register_id)
        queryset = UserDetail.objects.filter(phone_number=register_id)
        print(queryset)
        for obj in queryset:
            bio = obj.bio
            first_name = obj.phone_number.first_name
            last_name = obj.phone_number.last_name
            email = obj.phone_number.email
            gender = obj.phone_number.gender
            date_of_birth = obj.phone_number.date_of_birth
            dob = str(date_of_birth)
            x = dob.split('-')
            y = str(timezone.now().date())
            current_year = y.split('-')
            age = int(current_year[0]) - int(x[0])
            job_profile = obj.phone_number.job_profile
            company_name = obj.phone_number.company_name
            qualification = obj.phone_number.qualification
            relationship_status = obj.phone_number.relationship_status
            interests = obj.interest
            fav_quote = obj.phone_number.fav_quote
            religion = obj.phone_number.religion
            body_type = obj.phone_number.body_type
            zodiac_sign = obj.phone_number.zodiac_sign
            hashtag = obj.phone_number.zodiac_sign
            hashtag = obj.phone_number.hashtag
            verified = obj.phone_number.verified
            fb_signup = obj.phone_number.fb_signup
            if obj.phone_number.pic_1:
                pic_1 = obj.phone_number.pic_1.url
            else:
                pic_1 = ''
            if obj.phone_number.pic_2:
                pic_2 = obj.phone_number.pic_2.url
            else:
                pic_2 = ''
            if obj.phone_number.pic_3:
                pic_3 = obj.phone_number.pic_3.url
            else:
                pic_3 = ''
            if obj.phone_number.pic_4:
                pic_4 = obj.phone_number.pic_4.url
            else:
                pic_4 = ''
            if obj.phone_number.pic_5:
                pic_5 = obj.phone_number.pic_5.url
            else:
                pic_5 = ''
            if obj.phone_number.pic_6:
                pic_6 = obj.phone_number.pic_6.url
            else:
                pic_6 = ''
            # if obj.phone_number.pic_7:
            #     pic_7 = obj.phone_number.pic_7.url
            # else:
            #     pic_7 = ''
            # if obj.phone_number.pic_8:
            #     pic_8 = obj.phone_number.pic_8.url
            # else:
            #     pic_8 = ''
            # if obj.phone_number.pic_9:
            #     pic_9 = obj.phone_number.pic_9.url
            # else:
            #     pic_9 = ''
            living_in = obj.living_in
            hometown = obj.hometown
            profession = obj.profession
            college_name = obj.college_name
            university = obj.university
            personality = obj.personality
            preference_first_date = obj.preference_first_date
            fav_music = obj.fav_music
            travelled_place = obj.travelled_place
            once_in_life = obj.once_in_life
            exercise = obj.exercise
            looking_for = obj.looking_for
            food_type = obj.food_type
            owns = obj.owns
            fav_food = obj.fav_food
            fav_pet = obj.fav_pet
            smoke = obj.smoke
            drink = obj.drink
            subscription_purchased = obj.subscription_purchased
            subscription_purchased_at = obj.subscription_purchased_at
            discovery = obj.discovery
            distance_range = obj.distance_range
            min_age_range = obj.min_age_range
            max_age_range = obj.max_age_range
            # subscription = obj.subscription.values()
            detail = {
                "bio": bio,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "gender": gender,
                "date_of_birth": date_of_birth,
                "age": age,
                "job_profile": job_profile,
                "company_name": company_name,
                "qualification": qualification,
                "relationship_status": relationship_status,
                "interests": interests,
                "height": obj.phone_number.height,
                "fav_quote": fav_quote,
                "religion": religion,
                "body_type": body_type,
                "verified": verified,
                "fb_signup": fb_signup,
                "pic_1": pic_1,
                "pic_2": pic_2,
                "pic_3": pic_3,
                "pic_4": pic_4,
                "pic_5": pic_5,
                "pic_6": pic_6,
                # "pic_7": pic_7,
                # "pic_8": pic_8,
                # "pic_9": pic_9,
                "living_in": living_in,
                "hometown": hometown,
                "profession": profession,
                "college_name": college_name,
                "university": university,
                "personality": personality,
                "preference_first_date": preference_first_date,
                "fav_music": fav_music,
                "travelled_place": travelled_place,
                "once_in_life": once_in_life,
                "exercise": exercise,
                "looking_for": looking_for,
                "food_type": food_type,
                "owns": owns,
                "fav_food": fav_food,
                "fav_pet": fav_pet,
                "smoke": smoke,
                "drink": drink,
                "subscription_purchased": subscription_purchased,
                "discovery_lat": discovery[0],
                "discovery_lang": discovery[1],
                "distance_range": distance_range,
                "min_age_range": min_age_range,
                "max_age_range": max_age_range,
                "zodiac_sign": zodiac_sign,
                "hashtag": hashtag,
                # "deactivated": account.deactivated
                # "subscription": subscription
            }
            return Response({"Details": detail, 'status': HTTP_200_OK})
        return Response({"Details": queryset, 'status': HTTP_200_OK})


class SnippetFilter(rest_framework.FilterSet):
    qualification = rest_framework.CharFilter(lookup_expr='exact')
    relationship_status = rest_framework.CharFilter(lookup_expr='exact')
    religion = rest_framework.CharFilter(lookup_expr='exact')
    body_type = rest_framework.CharFilter(lookup_expr='exact')
    gender = rest_framework.CharFilter(lookup_expr='exact')
    interests = rest_framework.CharFilter(lookup_expr='exact')

    class Meta:
        model = RegisterUser
        fields = ['qualification', 'relationship_status',
                  'religion', 'body_type', 'gender', 'interests']
        # fileds = {
        #     'qualification': ['icontains'],
        #     'relationship_status': ['icontains'],
        #     'religion': ['icontains'],
        #     'body_type': ['icontains'],
        #     'gender': ['icontains'],
        #     'interests': ['icontains'],
        #
        # }


class SearchUser(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = SearchSerializer

    def post(self, request, *args, **kwargs):
        data = self.request.data
        # print('>>>>>>>>>>>>>>>>>',data)
        qualification = self.request.data['qualification']
        relationship_status = self.request.data['relationship_status']
        religion = self.request.data['religion']
        body_type = self.request.data['body_type']
        gender = self.request.data['gender']
        height = self.request.data['height']
        zodiac_sign = self.request.data['zodiac_sign']
        taste = self.request.data['taste']
        # qualification = self.request.POST.get('qualification', None)
        # relationship_status = self.request.POST.get('relationship_status', None)
        # religion = self.request.POST.get('religion', None)
        # body_type = self.request.POST.get('body_type', None)
        # gender = self.request.POST.get('gender', None)
        # interests = self.request.POST.get('interests', None)
        if data:
            qs = RegisterUser.objects.filter(Q(qualification__exact=qualification) |
                                             Q(relationship_status__exact=relationship_status) |
                                             Q(height__exact=height) |
                                             Q(gender__exact=gender) |
                                             Q(religion__exact=religion) |
                                             Q(zodiac_sign__exact=zodiac_sign) |
                                             Q(body_type__exact=body_type) |
                                             Q(taste__exact=taste)
                                             ).values()
            return Response({"data": qs, "status": HTTP_200_OK})


@method_decorator(csrf_exempt, name='dispatch')
class LikeUserAPIView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = LikeSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print(r_user.id)
        users_liked_by_me = MatchedUser.objects.filter(user=r_user)
        users_liked_me = MatchedUser.objects.filter(liked_by_me=r_user)
        liked_by_me = self.request.data['liked_by_me']
        users_liked_by_me_list = []
        users_liked_me_list = []
        for x in users_liked_me:
            if x.liked_by_me.all():
                print('Many to Many field ', x.liked_by_me.all()[0].id)
                print('LIKED BY USER', x.user.id)
                users_liked_me_list.append(x.user.id)
        for x in users_liked_by_me:
            if x.liked_by_me.all():
                users_liked_by_me_list.append(x.liked_by_me.all()[0].id)
        print('USERS LIKED BY ME LIST ', users_liked_by_me_list)
        print('USERS LIKED ME LIST', users_liked_me_list)
        print(liked_by_me)
        print(type(liked_by_me))
        print(users_liked_me_list + users_liked_by_me_list)
        print(int(liked_by_me) in users_liked_me_list + users_liked_by_me_list)
        if int(liked_by_me) not in users_liked_by_me_list + users_liked_me_list:
            register_user = RegisterUser.objects.get(id=r_user.id)
            from_user_name = register_user.first_name
            user = MatchedUser.objects.create(user=register_user, matched='No')
            user.liked_by_me.add(RegisterUser.objects.get(id=int(liked_by_me)))
            to_user_id = RegisterUser.objects.get(id=int(liked_by_me))
            UserNotification.objects.create(
                to=User.objects.get(email=to_user_id.email),
                title='Like Notification',
                body="You have been liked by " + from_user_name,
                extra_text=f'{register_user.id}'
            )
            fcm_token = User.objects.get(email=to_user_id.email).device_token
            print('FCM TOKEN ', fcm_token)

            try:
                # data_message = {"data": {"title": "Like Notification",
                #                          "body": "You have been liked by " + from_user_name,
                #                          "type": "likeNotification"}}
                title = "Like Notification"
                body = "You have been liked by " + from_user_name
                message_type = "likeNotification"
                # respo = send_to_one(fcm_token, data_message)
                respo = send_another(fcm_token, title, body)
                print("FCM Response===============>0", respo)
            except Exception as e:
                pass
            return Response({"message": "You have liked a user", "status": HTTP_200_OK})
        else:
            try:
                try:
                    m = MatchedUser.objects.get(user=r_user, matched='Yes', liked_by_me=int(liked_by_me))
                    print(m.id)
                    return Response({'message': 'You have already matched with this user', 'status': HTTP_200_OK})
                except Exception as e:
                    m = MatchedUser.objects.get(user=r_user, liked_by_me=int(liked_by_me))
                    print(m.id)
                    return Response({'message': 'You have already matched with this user', 'status': HTTP_200_OK})
            except Exception as e:
                print(e)
                register_user = RegisterUser.objects.get(id=r_user.id)
                from_user_name = register_user.first_name
                user = MatchedUser.objects.create(user=register_user, matched='Yes')
                user.liked_by_me.add(RegisterUser.objects.get(id=int(liked_by_me)))
                to_user_id = RegisterUser.objects.get(id=int(liked_by_me))
                # to_user_name = to_user_id.first_name
                UserNotification.objects.create(
                    to=User.objects.get(email=to_user_id.email),
                    title='Match Notification',
                    body="You have been matched by " + from_user_name,
                    extra_text=f'{register_user.id}'
                )
                fcm_token = User.objects.get(email=to_user_id.email).device_token
                try:
                    title = "Match Notification"
                    body = "You have been matched with " + from_user_name
                    message_type = "matchNotification"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
                return Response({"message": "You have matched with a user", "status": HTTP_200_OK})


@method_decorator(csrf_exempt, name='dispatch')
class DislikeUser(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser

    def post(self, request, *args, **kwargs):
        user = self.request.user
        logged_in_user_id = RegisterUser.objects.get(email=user.email)
        disliked_by_me = self.request.data['disliked_by_me']
        register_user = RegisterUser.objects.get(id=logged_in_user_id.id)
        from_user_name = register_user.first_name
        user = MatchedUser.objects.create(user=register_user, matched='No')
        user.disliked_by_me.add(RegisterUser.objects.get(id=int(disliked_by_me)))
        to_user_id = RegisterUser.objects.get(id=int(disliked_by_me))
        return Response({'message': 'Disliked user', 'status': HTTP_200_OK})


@method_decorator(csrf_exempt, name='dispatch')
class SuperLikeUserAPIView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = SuperLikeSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print(r_user.id)
        users_liked_by_me = MatchedUser.objects.filter(user=r_user)
        users_liked_me = MatchedUser.objects.filter(super_liked_by_me=r_user)
        super_liked_by_me = self.request.data['super_liked_by_me']
        users_liked_by_me_list = []
        users_liked_me_list = []
        for x in users_liked_me:
            if x.super_liked_by_me.all():
                print('Many to Many field ', x.super_liked_by_me.all()[0].id)
                print('LIKED BY USER', x.user.id)
                users_liked_me_list.append(x.user.id)
        for x in users_liked_by_me:
            if x.super_liked_by_me.all():
                users_liked_by_me_list.append(x.super_liked_by_me.all()[0].id)
        print('USERS LIKED BY ME LIST ', users_liked_by_me_list)
        print('USERS LIKED ME LIST', users_liked_me_list)
        print(super_liked_by_me)
        print(type(super_liked_by_me))
        print(users_liked_me_list + users_liked_by_me_list)
        print(int(super_liked_by_me) in users_liked_me_list + users_liked_by_me_list)
        if int(super_liked_by_me) not in users_liked_by_me_list + users_liked_me_list:
            register_user = RegisterUser.objects.get(id=r_user.id)
            from_user_name = register_user.first_name
            user = MatchedUser.objects.create(user=register_user, super_matched='No')
            user.super_liked_by_me.add(RegisterUser.objects.get(id=int(super_liked_by_me)))
            to_user_id = RegisterUser.objects.get(id=int(super_liked_by_me))
            UserNotification.objects.create(
                to=User.objects.get(email=to_user_id.email),
                title='Super Match Notification',
                body="You have been super liked by " + from_user_name,
                extra_text=f'{register_user.id}'
            )
            fcm_token = User.objects.get(email=to_user_id.email).device_token
            try:
                title = "Super Like Notification"
                body = "You have been super liked by " + from_user_name
                message_type = "superLike"
                respo = send_another(fcm_token, title, body)
                print("FCM Response===============>0", respo)
            except Exception as e:
                pass
            return Response({"message": "You have super liked a user", "status": HTTP_200_OK})
        else:
            try:
                try:
                    m = MatchedUser.objects.get(user=r_user, super_matched='Yes',
                                                super_liked_by_me=int(super_liked_by_me))
                    print(m.id)
                    print(m.super_matched)
                    return Response({'message': 'You have already super matched with this user', 'status': HTTP_200_OK})
                except Exception as e:
                    m = MatchedUser.objects.get(user=r_user, super_liked_by_me=int(super_liked_by_me))
                    print('--', m.id)
                    print(m.super_matched)
                    return Response({'message': 'You have already super liked this user', 'status': HTTP_200_OK})
            except Exception as e:
                print(e)
                register_user = RegisterUser.objects.get(id=r_user.id)
                from_user_name = register_user.first_name
                user = MatchedUser.objects.create(user=register_user, super_matched='Yes')
                user.super_liked_by_me.add(RegisterUser.objects.get(id=int(super_liked_by_me)))
                to_user_id = RegisterUser.objects.get(id=int(super_liked_by_me))
                # to_user_name = to_user_id.first_name
                UserNotification.objects.create(
                    to=User.objects.get(email=to_user_id.email),
                    title='Super Match Notification',
                    body="You have been super matched by " + from_user_name,
                    extra_text=f'{register_user.id}'
                )
                fcm_token = User.objects.get(email=to_user_id.email).device_token
                try:
                    title = "Super Like Notification"
                    body = "You have been super matched with " + from_user_name
                    message_type = "superMatch"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
                return Response({"message": "You have super matched with a user", "status": HTTP_200_OK})


class GetMatchesAPIView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = MatchedUserSerializer

    def get(self, request, *args, **kwargs):
        user_id = self.request.user
        r_user = RegisterUser.objects.get(email=user_id.email)
        match_with = MatchedUser.objects.filter(liked_by_me=r_user, matched='Yes').distinct()
        match_by = MatchedUser.objects.filter(user=r_user, matched='Yes').distinct()
        super_match_with = MatchedUser.objects.filter(super_liked_by_me=r_user, super_matched='Yes').distinct()
        super_match_by = MatchedUser.objects.filter(user=r_user, super_matched='Yes').distinct()
        users_blocked_by_me = BlockedUsers.objects.filter(user=r_user)
        print('USERS BLOCKED BY ME ', users_blocked_by_me)
        # users_blocked_by_me_list_2 = [x for x in users_blocked_by_me for y in x.blocked.all()]
        # print('BLOCKED LIST 2', users_blocked_by_me_list_2)
        users_blocked_by_me_list = []
        for user in users_blocked_by_me:
            for u in user.blocked.all():
                users_blocked_by_me_list.append(u.id)
        print('USERS BLOCKED BY ME LIST---', users_blocked_by_me_list)
        users_blocked_me = BlockedUsers.objects.filter(blocked=r_user)
        print('USERS BLOCKED ME ID', [x.user.id for x in users_blocked_me])
        # users_blocked_me_list = [x.id for x in users_blocked_me.blocked.all()]
        users_blocked_me_list = []
        for user in users_blocked_me:
            users_blocked_me_list.append(user.user.id)
        print('USERS BLOCKED ME ', users_blocked_me_list)
        final_blocked_users_list = users_blocked_by_me_list + users_blocked_me_list
        print('FINAL BLOCKED LIST', final_blocked_users_list)
        z = []
        a = []
        for y in match_with | match_by:
            try:
                if y.user.id == r_user.id:
                    if y.liked_by_me.all().last().id in final_blocked_users_list:
                        z.append(
                            {'match_id': y.id, 'id': y.liked_by_me.all().last().id,
                             'first_name': RegisterUser.objects.get(
                                 id=y.liked_by_me.all().last().id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.liked_by_me.all().last().id).last_name,
                             'profile_pic': RegisterUser.objects.get(
                                 id=y.liked_by_me.all().last().id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'match', 'blocked': True})
                    else:
                        z.append(
                            {'match_id': y.id, 'id': y.liked_by_me.all().last().id,
                             'first_name': RegisterUser.objects.get(
                                 id=y.liked_by_me.all().last().id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.liked_by_me.all().last().id).last_name,
                             'profile_pic': RegisterUser.objects.get(
                                 id=y.liked_by_me.all().last().id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'match', 'blocked': False})
                else:
                    if y.user.id in final_blocked_users_list:
                        z.append(
                            {'match_id': y.id, 'id': y.user.id,
                             'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=y.user.id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'match', 'blocked': True})
                    else:
                        z.append(
                            {'match_id': y.id, 'id': y.user.id,
                             'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=y.user.id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'match', 'blocked': False})

            except Exception as e:
                # print('EXCEPT BLOCK Match--------------', len(match_with | match_by))
                # print('ID BLOCK Match--------------', [x.id for x in y.liked_by_me.all()])
                if len(match_with | match_by) > 0:
                    try:
                        if y.user.id == r_user.id:
                            if y.liked_by_me.all().last().id in final_blocked_users_list:
                                z.append(
                                    {'match_id': y.id, 'id': y.liked_by_me.all().last().id,
                                     'first_name': RegisterUser.objects.get(
                                         id=y.liked_by_me.all().last().id).first_name,
                                     'last_name': RegisterUser.objects.get(
                                         id=y.liked_by_me.all().last().id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'match', 'blocked': True})
                            else:
                                z.append(
                                    {'match_id': y.id, 'id': y.liked_by_me.all().last().id,
                                     'first_name': RegisterUser.objects.get(
                                         id=y.liked_by_me.all().last().id).first_name,
                                     'last_name': RegisterUser.objects.get(
                                         id=y.liked_by_me.all().last().id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'match', 'blocked': False})
                        else:
                            if y.user.id in final_blocked_users_list:
                                z.append(
                                    {'match_id': y.id, 'id': y.user.id,
                                     'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                                     'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'match', 'blocked': True})
                            else:
                                z.append(
                                    {'match_id': y.id, 'id': y.user.id,
                                     'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                                     'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'match', 'blocked': False})
                    except Exception as e:
                        print(e)
                        pass
                else:
                    pass

        for y in super_match_with | super_match_by:
            try:
                if y.user.id == r_user.id:
                    if y.super_liked_by_me.all().last().id in final_blocked_users_list:
                        a.append(
                            {'match_id': y.id, 'id': y.super_liked_by_me.all().last().id,
                             'first_name': RegisterUser.objects.get(
                                 id=y.super_liked_by_me.all().last().id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.super_liked_by_me.all().last().id).last_name,
                             'profile_pic': RegisterUser.objects.get(
                                 id=y.super_liked_by_me.all().last().id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'super_match', 'blocked': True})
                    else:
                        a.append(
                            {'match_id': y.id, 'id': y.super_liked_by_me.all().last().id,
                             'first_name': RegisterUser.objects.get(
                                 id=y.super_liked_by_me.all().last().id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.super_liked_by_me.all().last().id).last_name,
                             'profile_pic': RegisterUser.objects.get(
                                 id=y.super_liked_by_me.all().last().id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'super_match', 'blocked': False})
                else:
                    if y.user.id in final_blocked_users_list:
                        a.append(
                            {'match_id': y.id, 'id': y.user.id,
                             'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=y.user.id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'super_match', 'blocked': True})
                    else:
                        a.append(
                            {'match_id': y.id, 'id': y.user.id,
                             'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                             'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=y.user.id).pic_1.url,
                             'matched_at': y.matched_at,
                             'type': 'super_match', 'blocked': False})
            except Exception as e:
                try:
                    print('EXCEPT BLOCK Match--------------', y)
                    if len(super_match_with | super_match_by) > 0:
                        if y.user.id == r_user.id:
                            if y.super_liked_by_me.all().last().id in final_blocked_users_list:
                                z.append(
                                    {'match_id': y.id, 'id': y.super_liked_by_me.all().last().id,
                                     'first_name': RegisterUser.objects.get(
                                         id=y.super_liked_by_me.all().last().id).first_name,
                                     'last_name': RegisterUser.objects.get(
                                         id=y.super_liked_by_me.all().last().id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'super_match', 'block': True})
                            else:
                                z.append(
                                    {'match_id': y.id, 'id': y.super_liked_by_me.all().last().id,
                                     'first_name': RegisterUser.objects.get(
                                         id=y.super_liked_by_me.all().last().id).first_name,
                                     'last_name': RegisterUser.objects.get(
                                         id=y.super_liked_by_me.all().last().id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'super_match', 'block': False})
                        else:
                            if y.user.id in final_blocked_users_list:
                                a.append(
                                    {'match_id': y.id, 'id': y.user.id,
                                     'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                                     'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'super_match', 'blocked': True})
                            else:
                                a.append(
                                    {'match_id': y.id, 'id': y.user.id,
                                     'first_name': RegisterUser.objects.get(id=y.user.id).first_name,
                                     'last_name': RegisterUser.objects.get(id=y.user.id).last_name,
                                     'profile_pic': '',
                                     'matched_at': y.matched_at,
                                     'type': 'super_match', 'blocked': False})
                    else:
                        pass
                except Exception as e:
                    pass
        return Response({'match': z + a, 'status': HTTP_200_OK})


class UserLikedList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        like_list = []
        super_like_list = []
        liked_users = MatchedUser.objects.filter(liked_by_me=r_user)
        print('LIKED USERS ', liked_users)
        print('LIKED USERS ', len(liked_users))
        super_liked_users = MatchedUser.objects.filter(super_liked_by_me=r_user)
        print('SUPER LIKED USERS', super_liked_users)
        print('SUPER LIKED USERS', len(super_liked_users))
        for z in liked_users:
            if len(liked_users) > 0:
                # print(user.liked_by_me.all()[0].id)
                # print(user.liked_by_me.all().first().id)
                # z = RegisterUser.objects.get(id=user.id)
                if z.id not in like_list:
                    print(z.id)
                    if z.user.pic_1:
                        like_list.append(
                            {'id': z.user.id, 'first_name': z.user.first_name, 'last_name': z.user.last_name,
                             'liked_at': z.matched_at,
                             'profile_pic': z.user.pic_1.url, 'type': 'like'})
                    else:
                        like_list.append(
                            {'id': z.user.id, 'first_name': z.user.first_name, 'last_name': z.user.last_name,
                             'liked_at': z.matched_at,
                             'profile_pic': '', 'type': 'like'})
                else:
                    pass
        for y in super_liked_users:
            if len(super_liked_users) > 0:
                # print(user.super_liked_by_me.all()[0].id)
                # print(user.super_liked_by_me.all().first().id)
                # z = RegisterUser.objects.get(id=user.super_liked_by_me.all().first().id)
                # for y in super_liked_users:
                if y.id not in super_like_list:
                    print(y.id)
                    if y.user.pic_1:
                        super_like_list.append(
                            {'id': y.user.id, 'first_name': y.user.first_name, 'last_name': y.user.last_name,
                             'liked_at': y.matched_at,
                             'profile_pic': y.user.pic_1.url, 'type': 'super_like'})
                    else:
                        super_like_list.append(
                            {'id': y.id, 'first_name': y.user.first_name, 'last_name': y.user.last_name,
                             'liked_at': y.matched_at,
                             'profile_pic': '', 'type': 'super_like'})
                else:
                    pass
        return Response({'data': like_list + super_like_list, 'status': HTTP_200_OK})


class LikedUserCount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        liked_users = MatchedUser.objects.filter(liked_by_me=r_user)
        print('LIKED USERS ', liked_users)
        print('LIKED USERS ', len(liked_users))
        super_liked_users = MatchedUser.objects.filter(super_liked_by_me=r_user)
        print('SUPER LIKED USERS ', super_liked_users)
        print('SUPER LIKED USERS ', len(super_liked_users))
        return Response({'message': 'Like count fetched successfully', 'count': len(liked_users | super_liked_users),
                         'verified': r_user.verified,
                         'status': HTTP_200_OK})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteMatchesAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = DeleteMatchSerializer

    def get(self, request, *args, **kwargs):
        logged_in_user_id = self.request.data['id']
        liked_by_me = MatchedUser.objects.filter(
            liked_by_me=logged_in_user_id).values()
        return Response({"LikedUsers": liked_by_me}, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        liked = self.request.data['liked_by_me']
        logged_in_user_id = self.request.data['id']
        liked_by_me = MatchedUser.objects.filter(liked_by_me=logged_in_user_id)
        liked = int(liked)
        x = []
        for obj in liked_by_me:
            y = obj.user.id
            x.append(y)
        if liked and liked in x:
            MatchedUser.objects.filter(liked_by_me=liked).delete()
            return Response({"User removed successfully"}, status=HTTP_200_OK)
        else:
            return Response({"Cannot be removed. User is not a match"}, status=HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteSuperMatchesAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = DeleteSuperMatchSerializer

    def get(self, request, *args, **kwargs):
        data = self.request.data
        logged_in_user_id = self.request.data['id']
        super_liked_by_me = MatchedUser.objects.filter(
            super_liked_by_me=logged_in_user_id).values()
        return Response({"SuperLiked Users": super_liked_by_me}, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = self.request.data
        # id = self.request.data['id']
        logged_in_user_id = self.request.data['id']
        super_liked = self.request.data['super_liked_by_me']
        super_liked_by_me = MatchedUser.objects.filter(
            super_liked_by_me=logged_in_user_id)
        super_liked = int(super_liked)
        x = []
        for obj in super_liked_by_me:
            y = obj.user.id
            x.append(y)
        if super_liked and super_liked in x:
            MatchedUser.objects.filter(super_liked_by_me=super_liked).delete()
            return Response({"User removed successfully"}, status=HTTP_200_OK)
        else:
            return Response({"User cannot be removed. User is not a super match"}, status=HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class RequestMeetingAPIView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = RequestMeeting
    serializer_class = RequestMeetingSerializer

    def post(self, request, *args, **kwargs):
        print('_____________', self.request.data)
        phone_number = self.request.data['phone_number']
        logged_in_user_id = self.request.data['id']
        requested_user = RegisterUser.objects.get(id=phone_number)
        from_id = logged_in_user_id
        from_user_id = RegisterUser.objects.get(id=from_id)
        from_user_name = from_user_id.first_name
        phone_number = self.request.data['phone_number']
        to_user = RegisterUser.objects.get(id=phone_number)
        first_name = to_user.first_name
        to_id = self.request.data['phone_number']
        to_user_id = RegisterUser.objects.get(id=to_id)
        liked_by_me = MatchedUser.objects.filter(liked_by_me=logged_in_user_id)
        super_liked_by_me = MatchedUser.objects.filter(
            super_liked_by_me=logged_in_user_id)
        liked_by = MatchedUser.objects.filter(liked_by=logged_in_user_id)
        super_liked_by = MatchedUser.objects.filter(
            super_liked_by=logged_in_user_id)
        liked_by_list = [x.id for x in liked_by]
        super_liked_by_list = [x.id for x in super_liked_by]
        liked_by_me_list = [x.id for x in liked_by_me]
        super_liked_by_me_list = [x.id for x in super_liked_by_me]
        if requested_user in liked_by_list and requested_user in liked_by_me_list:
            RequestMeeting.objects.create(
                phone_number=requested_user
            )
            UserNotification.objects.create(
                from_user_id=from_user_id,
                from_user_name=from_user_name,
                to_user_id=to_user_id,
                to_user_name=first_name,
                notification_type="Meeting",
                notification_title="Meeting request",
                notification_body="You have a meeting request from " + first_name,
                extra_text=f'{from_user_id.id}'
            )
            return Response({"Request sent successfully"}, status=HTTP_200_OK)
        else:
            return Response({"Cannot send request as the user is not a match"}, status=HTTP_400_BAD_REQUEST)


class UpdateMeeting(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        meeting_id = self.request.POST['meeting_id']
        meeting_date = self.request.POST['meeting_date']
        meeting_time = self.request.POST['meeting_time']
        venue = self.request.POST['venue']
        description = self.request.POST['description']
        user = self.request.user
        print('user', user)
        logged_in_user_id = RegisterUser.objects.get(email=user.email)
        print('Logged in user', logged_in_user_id)
        try:
            meeting_obj = ScheduleMeeting.objects.get(id=meeting_id)
            meeting_obj.meeting_date = meeting_date
            meeting_obj.meeting_time = meeting_time
            meeting_obj.venue = venue
            meeting_obj.description = description
            meeting_obj.status = 'Not Completed'
            meeting_obj.save()
            scheduled_with = meeting_obj.scheduled_with
            scheduled_by = meeting_obj.scheduled_by
            print(scheduled_with, scheduled_by)
            print('scheduled with ', User.objects.get(email=scheduled_with.email))
            print('schedule by ', User.objects.get(email=scheduled_by.email))
            if logged_in_user_id == scheduled_with:
                UserNotification.objects.create(
                    to=User.objects.get(email=scheduled_by.email),
                    title='Meeting Request',
                    body="Your meeting has been updated by " + scheduled_with.first_name,
                    extra_text=f'{scheduled_with.id}'
                )
                fcm_token = User.objects.get(email=scheduled_by.email).device_token
                try:
                    title = "Meeting Request"
                    body = "Your meeting has been updated by " + scheduled_with.first_name
                    message_type = "meeting"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
            else:
                UserNotification.objects.create(
                    to=User.objects.get(email=scheduled_with.email),
                    title='Meeting Request',
                    body="Your meeting has been updated by " + scheduled_by.first_name,
                    extra_text=f'{scheduled_by.id}'
                )
                fcm_token = User.objects.get(email=scheduled_with.email).device_token
                try:
                    title = "Meeting Request"
                    body = "Your meeting has been updated by " + logged_in_user_id.first_name
                    message_type = "meeting"
                    respo = send_another(fcm_token, title, body)
                    print("FCM Response===============>0", respo)
                except Exception as e:
                    pass
            return Response({'message': 'Meeting updated successfully', 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class MeetingStatusAPIView(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = RequestMeeting
    serializer_class = MeetingStatusSerializer
    queryset = RequestMeeting.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = request.data.get("status")
        instance.save(update_fields=['status'])
        logged_in_user_id = self.request.data['id']
        from_id = logged_in_user_id
        from_user_id = RegisterUser.objects.get(id=from_id)
        from_user_name = from_user_id.first_name
        phone_number = self.request.data['phone_number']
        to_user = RegisterUser.objects.get(id=phone_number)
        first_name = to_user.first_name
        to_id = self.request.data['phone_number']
        to_user_id = RegisterUser.objects.get(id=to_id)
        status = self.request.data['status']

        UserNotification.objects.create(
            from_user_id=from_user_id,
            from_user_name=from_user_name,
            to_user_id=to_user_id,
            to_user_name=first_name,
            notification_type='Meeting Status',
            notification_title='Meeting Status Update',
            notification_body='Your meeting request status with ' +
                              from_user_name + ' has changed to  ' + status,
            extra_text=f'{from_user_id.id}'
        )
        return Response({"Meeting status has been updated successfully"}, status=HTTP_200_OK)


class ScheduleMeetingAPIView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ScheduleMeeting
    serializer_class = ScheduleMeetingSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        phone_number = self.request.data['id']
        # to_id = self.request.data['phone_number']
        # logged_in_user_id = self.request.data['id']
        logged_in_user_id = RegisterUser.objects.get(email=user.email)
        requested_user = RegisterUser.objects.get(id=int(phone_number))
        scheduled_by = RegisterUser.objects.get(email=user.email)
        meeting_date = self.request.data['meeting_date']
        meeting_time = self.request.data['meeting_time']
        venue = self.request.data['venue']
        description = self.request.data['description']
        status = self.request.data['status']
        from_id = requested_user.id
        from_user_id = RegisterUser.objects.get(id=from_id)
        from_user_name = from_user_id.first_name
        meeting = ScheduleMeeting.objects.create(
            scheduled_with=requested_user,
            scheduled_by=scheduled_by,
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            venue=venue,
            description=description,
            status=status
        )
        UserNotification.objects.create(
            to=User.objects.get(email=requested_user.email),
            title='Meeting Request',
            body="You have a meeting request from " + logged_in_user_id.first_name,
            extra_text=f'{from_user_id.id}'
        )
        fcm_token = User.objects.get(email=requested_user.email).device_token
        try:
            title = "Meeting Request"
            body = "You have a meeting request from " + logged_in_user_id.first_name
            message_type = "meeting"
            respo = send_another(fcm_token, title, body)
            print("FCM Response===============>0", respo)
        except Exception as e:
            pass
        return Response(
            {"meeting_id": meeting.id, "message": "Meeting schedule sent successfully", 'status': HTTP_200_OK})


class MeetingDetail(APIView):
    model = ScheduleMeeting
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user_id = self.request.user
        r_user = RegisterUser.objects.get(email=user_id.email)
        meeting_id = self.request.data['meeting_id']
        meeting_obj = ScheduleMeeting.objects.get(id=meeting_id)
        match_with = MatchedUser.objects.filter(liked_by_me=meeting_obj.scheduled_by, matched='Yes').distinct()
        match_by = MatchedUser.objects.filter(user=meeting_obj.scheduled_with, matched='Yes').distinct()
        for y in match_with | match_by:
            print(y, r_user.id)
            print(y.user, r_user.id, [x.id for x in y.liked_by_me.all()], y.matched)
            print(meeting_obj.scheduled_with.id, meeting_obj.scheduled_with.id in [x.id for x in y.liked_by_me.all()],
                  meeting_obj.scheduled_by.id, meeting_obj.scheduled_by.id in [x.id for x in y.liked_by_me.all()])
            if meeting_obj.scheduled_with.id in [x.id for x in
                                                 y.liked_by_me.all()] or meeting_obj.scheduled_by.id in [x.id for x in
                                                                                                         y.liked_by_me.all()]:
                if meeting_obj.scheduled_by.pic_1 and meeting_obj.scheduled_with.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id,
                         'invited_by_pic': meeting_obj.scheduled_by.pic_1.url,
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id,
                         'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK, 'matched_at': y.matched_at})
                elif not meeting_obj.scheduled_by.pic_1 and not meeting_obj.scheduled_with.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': '',
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK, 'matched_at': y.matched_at})
                elif meeting_obj.scheduled_by.pic_1 and not meeting_obj.scheduled_with.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id,
                         'invited_by_pic': meeting_obj.scheduled_by.pic_1.url,
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': '',
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK, 'matched_at': y.matched_at})
                elif meeting_obj.scheduled_with.pic_1 and not meeting_obj.scheduled_by.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id,
                         'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK, 'matched_at': y.matched_at})
                else:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id,
                         'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK, 'matched_at': y.matched_at})
            else:
                if meeting_obj.scheduled_by.pic_1 and meeting_obj.scheduled_with.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id,
                         'invited_by_pic': meeting_obj.scheduled_by.pic_1.url,
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id,
                         'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK})
                elif not meeting_obj.scheduled_by.pic_1 and not meeting_obj.scheduled_with.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': '',
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK})
                elif meeting_obj.scheduled_by.pic_1 and not meeting_obj.scheduled_with.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id,
                         'invited_by_pic': meeting_obj.scheduled_by.pic_1.url,
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': '',
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK})
                elif meeting_obj.scheduled_with.pic_1 and not meeting_obj.scheduled_by.pic_1:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id,
                         'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK})
                else:
                    return Response(
                        {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                         'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                         'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                         'invitee_id': meeting_obj.scheduled_with.id,
                         'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                         'invitee_first_name': meeting_obj.scheduled_with.first_name,
                         'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                         'date': meeting_obj.meeting_date, 'description': meeting_obj.description,
                         'venue': meeting_obj.venue,
                         'status': HTTP_200_OK, })


class MettingList(APIView):
    model = ScheduleMeeting
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        register_user = RegisterUser.objects.get(email=user.email)
        print(register_user.id)
        meeting_request_received = ScheduleMeeting.objects.filter(
            scheduled_with=RegisterUser.objects.get(email=user.email)).exclude(status='Rejected')
        meeting_request_sent = ScheduleMeeting.objects.filter(
            scheduled_by=RegisterUser.objects.get(email=user.email)).exclude(status='Rejected')
        users_blocked_by_me = BlockedUsers.objects.filter(user=register_user)
        print('USERS BLOCKED BY ME ', users_blocked_by_me)
        # users_blocked_by_me_list_2 = [x for x in users_blocked_by_me for y in x.blocked.all()]
        # print('BLOCKED LIST 2', users_blocked_by_me_list_2)
        users_blocked_by_me_list = []
        for user in users_blocked_by_me:
            for u in user.blocked.all():
                users_blocked_by_me_list.append(u.id)
        print('USERS BLOCKED BY ME LIST---', users_blocked_by_me_list)
        users_blocked_me = BlockedUsers.objects.filter(blocked=register_user)
        print('USERS BLOCKED ME ID', [x.user.id for x in users_blocked_me])
        # users_blocked_me_list = [x.id for x in users_blocked_me.blocked.all()]
        users_blocked_me_list = []
        for user in users_blocked_me:
            users_blocked_me_list.append(user.user.id)
        print('USERS BLOCKED ME ', users_blocked_me_list)
        final_blocked_users_list = users_blocked_by_me_list + users_blocked_me_list
        print('FINAL BLOCKED LIST', final_blocked_users_list)
        recevied_list = []
        sent_list = []
        for meeting in meeting_request_received:
            try:
                if RegisterUser.objects.get(id=meeting.scheduled_by.id).pic_1:
                    if RegisterUser.objects.get(id=meeting.scheduled_by.id).id in final_blocked_users_list:
                        recevied_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_by.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_by.id).pic_1.url,
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'received', 'blocked': True})
                    else:
                        recevied_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_by.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_by.id).pic_1.url,
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'received', 'blocked': False})
                else:
                    if RegisterUser.objects.get(id=meeting.scheduled_by.id).id in final_blocked_users_list:
                        recevied_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_by.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                             'profile_pic': '',
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'received', 'blocked': True})
                    else:
                        recevied_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_by.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                             'profile_pic': '',
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'received', 'blocked': False})
            except Exception as e:
                print(e)
                pass
        for meeting in meeting_request_sent:
            try:
                if RegisterUser.objects.get(id=meeting.scheduled_with.id).pic_1:
                    if RegisterUser.objects.get(id=meeting.scheduled_with.id).id in final_blocked_users_list:
                        sent_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_with.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_with.id).pic_1.url,
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'sent', 'blocked': True})
                    else:
                        sent_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_with.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                             'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_with.id).pic_1.url,
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'sent', 'blocked': False})
                else:
                    if RegisterUser.objects.get(id=meeting.scheduled_with.id).id in final_blocked_users_list:
                        sent_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_with.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                             'profile_pic': '',
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'sent', 'blocked': True})
                    else:
                        sent_list.append(
                            {'id': meeting.id,
                             'user_id': RegisterUser.objects.get(id=meeting.scheduled_with.id).id,
                             'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                             'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                             'profile_pic': '',
                             'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                             'type': 'sent', 'blocked': False})
            except Exception as e:
                print(e)
                pass
        return Response({'meetings': recevied_list + sent_list, 'status': HTTP_200_OK})


class UpdateMeetingStatus(APIView):
    model = ScheduleMeeting
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        status = self.request.POST['status']
        meeting_id = self.request.POST['meeting_id']
        meeting = ScheduleMeeting.objects.get(id=meeting_id)
        meeting.status = status.capitalize()
        meeting.save()
        UserNotification.objects.create(
            to=User.objects.get(email=meeting.scheduled_by.email),
            title='Meeting Status',
            body="Your meeting request has been {} by {}".format(status, meeting.scheduled_with.first_name),
            extra_text=f'{meeting.scheduled_with.id}'
        )
        fcm_token = User.objects.get(email=meeting.scheduled_by.email).device_token
        try:
            title = "Meeting Status"
            body = "Your meeting request has been {} by {}".format(status, meeting.scheduled_with.first_name)
            message_type = "superLike"
            respo = send_another(fcm_token, title, body)
            print("FCM Response===============>0", respo)
        except Exception as e:
            pass
        return Response({'message': 'Meeting status updated successfully', 'status': HTTP_200_OK})


class UpdateUserLocation(APIView):
    model = UserDetail
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        lat = self.request.POST['lat']
        lang = self.request.POST['lang']
        address = self.request.POST['address']
        r_user = RegisterUser.objects.get(email=self.request.user.email)
        user_detail = UserDetail.objects.get(phone_number=r_user)
        user_detail.discovery = fromstr(f'POINT({lang} {lat})', srid=4326)
        user_detail.address = address
        user_detail.save()
        return Response({'message': 'Location updated successfully', 'status': HTTP_200_OK})


class FeedbackApiView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Feedback
    serializer_class = FeedbackSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        reg_obj = RegisterUser.objects.get(email=user.email)
        serializer = FeedbackSerializer(data=self.request.data)
        if serializer.is_valid():
            stars = serializer.validated_data['stars']
            feedback = serializer.validated_data['feedback']
            Feedback.objects.create(
                phone_number=reg_obj,
                stars=stars,
                feedback=feedback
            )
            return Response({'message': 'Feedback submitted successfully', 'status': HTTP_200_OK})
        else:
            return Response({'error': serializer.errors, 'status': HTTP_400_BAD_REQUEST})


class FeedbackWithoutStar(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = FeedbackWithoutStars

    def post(self, request, *args, **kwargs):
        user = self.request.user
        reg_obj = RegisterUser.objects.get(email=user.email)
        feedback = self.request.POST['feedback']
        subject = self.request.POST['subject']
        FeedbackWithoutStars.objects.create(
            phone_number=reg_obj,
            feedback=feedback,
            subject=subject
        )
        return Response({'message': 'Feedback submitted successfully', 'status': HTTP_200_OK})


class ContactUsApiView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ContactUs
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()

    def get(self, request, *args, **kwargs):
        phone_number = ContactUs.objects.all().first().phone_number
        email = ContactUs.objects.all().first().email
        return Response(
            {'message': 'Contact us details fetched successfully', 'phone_number': phone_number, 'email': email,
             'status': HTTP_200_OK})


class ContactUsQueryForm(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ContactUsQuery

    def post(self, request, *args, **kwargs):
        user = self.request.user
        reg_obj = RegisterUser.objects.get(email=user.email)
        reason = self.request.POST['reason']
        description = self.request.POST['description']
        ContactUsQuery.objects.create(
            user=reg_obj,
            reason=reason,
            description=description
        )
        return Response({"message": "Query submitted successfully", "status": HTTP_200_OK})


class AboutUsApiView(ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = AboutUs
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()


class EditAboutUsAPIView(UpdateAPIView):
    model = AboutUs
    serializer_class = AboutUsSerializer
    queryset = AboutUs.objects.all()


class EditContactUsApiView(UpdateAPIView):
    model = ContactUs
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()


class CheckDob(APIView):

    def post(self, request, *args, **kwargs):
        social_id = self.request.POST['social_id']
        device_token = self.request.POST['device_token']
        try:
            user = User.objects.get(social_id=social_id)
            user.device_token = device_token
            user.save()
            user_data = RegisterUser.objects.get(email=user.email)
            user_with_token = Token.objects.get_or_create(user=user)
            user_with_token = user_with_token[0]
            print(user_with_token)
            user_detail = UserDetail.objects.get(phone_number=user_data)
            pic_1 = ''
            pic_2 = ''
            pic_3 = ''
            pic_4 = ''
            pic_5 = ''
            pic_6 = ''
            pic_7 = ''
            pic_8 = ''
            pic_9 = ''
            if user_data.pic_1:
                pic_1 = user_data.pic_1.url
            else:
                pic_1 = ''
            if user_data.pic_2:
                pic_2 = user_data.pic_2.url
            else:
                pic_2 = ''
            if user_data.pic_3:
                pic_3 = user_data.pic_3.url
            else:
                pic_3 = ''
            if user_data.pic_4:
                pic_4 = user_data.pic_4.url
            else:
                pic_4 = ''
            if user_data.pic_5:
                pic_5 = user_data.pic_5.url
            else:
                pic_5 = ''
            if user_data.pic_6:
                pic_6 = user_data.pic_6.url
            else:
                pic_6 = ''
            # if user_data.pic_7:
            #     pic_7 = user_data.pic_8.url
            # else:
            #     pic_7 = ''
            # if user_data.pic_8:
            #     pic_8 = user_data.pic_8.url
            # else:
            #     pic_8 = ''
            # if user_data.pic_9:
            #     pic_9 = user_data.pic_9.url
            # else:
            #     pic_9 = ''
            Data = {
                "id": user_data.id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "phone_number": user_data.phone_number,
                "gender": user_data.gender,
                "date_of_birth": user_data.date_of_birth,
                # "job_profile": user_data.job_profile,
                # "company_name": user_data.company_name,
                # "qualification": user_data.qualification,
                # "relationship_status": user_data.relationship_status,
                # "interests": user_data.interests,
                # "fav_quote": user_data.fav_quote,
                "pic_1": pic_1,
                "pic_2": pic_2,
                "pic_3": pic_3,
                "pic_4": pic_4,
                "pic_5": pic_5,
                "pic_6": pic_6,
                # "pic_7": pic_7,
                # "pic_8": pic_8,
                # "pic_9": pic_9,
                "discovery_lat": user_detail.discovery[0],
                "discovery_lang": user_detail.discovery[1],
                "distance_range": user_detail.distance_range,
                "min_age_range": user_detail.min_age_range,
                "max_age_range": user_detail.max_age_range,
                "interested": user_detail.interest
            }
            r_user = RegisterUser.objects.get(email=user.email)
            account = DeactivateAccount.objects.get(user=r_user)
            if account.deactivated:
                account.deactivated = False
                account.save()
                user_detail.deactivated = False
                user_detail.save()
            # return Response({"Token": user_with_token.key, "user_id": user.id, "status": HTTP_200_OK})
            return Response({'message': "User with this social id exists", 'exists': True, "Token": user_with_token.key,
                             'data': Data, 'deactivated': account.deactivated,
                             'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'exists': False, 'status': HTTP_400_BAD_REQUEST})


class FacebookSignupApiView(CreateAPIView):
    serializer_class = FacebookSerializer

    def post(self, request, *args, **kwargs):
        name = self.request.POST.get('name' or None)
        # last_name = self.request.POST.get('last_name' or None)
        email = self.request.POST.get('email' or None)
        social_id = self.request.POST.get('social_id' or None)
        social_type = self.request.POST.get('social_type' or None)
        profile_pic = self.request.POST.get('profile_pic' or None)
        device_token = self.request.POST.get('device_token' or None)
        lat = self.request.POST.get('lat' or None)
        lang = self.request.POST.get('lang' or None)
        dob = self.request.POST.get('dob' or None)

        # print('>>>>>>>>>>>>>>', device_token)
        print('before try')
        try:
            print('inside try')
            print('Email------------>>>', email)
            print('Email fb try------------>>>', self.request.data)
            user = User.objects.get(social_id=social_id)
            print('user', user)
            if user:
                user_with_token = Token.objects.get_or_create(user=user)
                print('token-->>', user_with_token)
                user.device_token = device_token
                print('from fb sign in device token ', device_token)
                user.save(update_fields=['device_token'])
                user_with_token = user_with_token[0]
                print(user_with_token)
                user_data = RegisterUser.objects.get(email=user.email)
                user_detail = UserDetail.objects.get(phone_number=user_data)
                pic_1 = ''
                pic_2 = ''
                pic_3 = ''
                pic_4 = ''
                pic_5 = ''
                pic_6 = ''
                pic_7 = ''
                pic_8 = ''
                pic_9 = ''
                if user_data.pic_1:
                    pic_1 = user_data.pic_1.url
                else:
                    pic_1 = ''
                if user_data.pic_2:
                    pic_2 = user_data.pic_2.url
                else:
                    pic_2 = ''
                if user_data.pic_3:
                    pic_3 = user_data.pic_3.url
                else:
                    pic_3 = ''
                if user_data.pic_4:
                    pic_4 = user_data.pic_4.url
                else:
                    pic_4 = ''
                if user_data.pic_5:
                    pic_5 = user_data.pic_5.url
                else:
                    pic_5 = ''
                if user_data.pic_6:
                    pic_6 = user_data.pic_6.url
                else:
                    pic_6 = ''
                # if user_data.pic_7:
                #     pic_7 = user_data.pic_8.url
                # else:
                #     pic_7 = ''
                # if user_data.pic_8:
                #     pic_8 = user_data.pic_8.url
                # else:
                #     pic_8 = ''
                # if user_data.pic_9:
                #     pic_9 = user_data.pic_9.url
                # else:
                #     pic_9 = ''
                Data = {
                    "id": user_data.id,
                    "email": user_data.email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "phone_number": user_data.phone_number,
                    "gender": user_data.gender,
                    "date_of_birth": user_data.date_of_birth,
                    # "job_profile": user_data.job_profile,
                    # "company_name": user_data.company_name,
                    # "qualification": user_data.qualification,
                    # "relationship_status": user_data.relationship_status,
                    # "interests": user_data.interests,
                    # "fav_quote": user_data.fav_quote,
                    "pic_1": pic_1,
                    "pic_2": pic_2,
                    "pic_3": pic_3,
                    "pic_4": pic_4,
                    "pic_5": pic_5,
                    "pic_6": pic_6,
                    # "pic_7": pic_7,
                    # "pic_8": pic_8,
                    # "pic_9": pic_9,
                    "discovery_lat": user_detail.discovery[0],
                    "discovery_lang": user_detail.discovery[1],
                    "distance_range": user_detail.distance_range,
                    "min_age_range": user_detail.min_age_range,
                    "max_age_range": user_detail.max_age_range,
                    "interested": user_detail.interest,
                    "verified": user_data.verified
                }
                r_user = RegisterUser.objects.get(email=user.email)
                account = DeactivateAccount.objects.get(user=r_user)
                if account.deactivated:
                    account.deactivated = False
                    account.save()
                    user_detail.deactivated = False
                    user_detail.save()
                return Response(
                    {"Token": user_with_token.key, "user_id": user_data.id, 'data': Data,
                     'deactivated': account.deactivated, "status": HTTP_200_OK})
        except:
            print('inside except')
            print('Email fb except------------>>>', self.request.data)
            serializer = FacebookSerializer(data=request.data)
            if serializer.is_valid():
                if profile_pic is not None and profile_pic != '':
                    pic = ''
                    data = ''
                    image_url = profile_pic
                    img_data = requests.get(image_url).content
                    with open(f'{social_id}.png', 'wb') as handler:
                        handler.write(img_data)
                        pic = handler.name
                    with open(os.path.abspath(pic), 'rb') as f:
                        print('FFFFFFFFFFFFFF_______________', f)
                        data = f.read()
                    reg_usr = RegisterUser.objects.create(
                        email=email,
                        first_name=name,
                        date_of_birth=dob,
                        verified=True
                    )
                    reg_usr.pic_1.save(f'{social_id}.png', ContentFile(data))
                    print(reg_usr.pic_1.url)
                    user = User.objects.create(
                        name=name,
                        # last_name=last_name,
                        email=email,
                        social_id=social_id,
                        social_type=social_type,
                        # profile_pic=profile_pic,
                        device_token=device_token,
                    )
                    UserDetail.objects.create(
                        phone_number=reg_usr,
                        discovery=fromstr(f'POINT({lang} {lat})', srid=4326)
                    )
                    DeactivateAccount.objects.create(
                        user=reg_usr
                    )
                    token = Token.objects.create(user=user)
                    user_data = RegisterUser.objects.get(email=user.email)
                    user_detail = UserDetail.objects.get(phone_number=user_data)
                    pic_1 = ''
                    pic_2 = ''
                    pic_3 = ''
                    pic_4 = ''
                    pic_5 = ''
                    pic_6 = ''
                    pic_7 = ''
                    pic_8 = ''
                    pic_9 = ''
                    if user_data.pic_1:
                        pic_1 = user_data.pic_1.url
                    else:
                        pic_1 = ''
                    if user_data.pic_2:
                        pic_2 = user_data.pic_2.url
                    else:
                        pic_2 = ''
                    if user_data.pic_3:
                        pic_3 = user_data.pic_3.url
                    else:
                        pic_3 = ''
                    if user_data.pic_4:
                        pic_4 = user_data.pic_4.url
                    else:
                        pic_4 = ''
                    if user_data.pic_5:
                        pic_5 = user_data.pic_5.url
                    else:
                        pic_5 = ''
                    if user_data.pic_6:
                        pic_6 = user_data.pic_6.url
                    else:
                        pic_6 = ''
                    # if user_data.pic_7:
                    #     pic_7 = user_data.pic_8.url
                    # else:
                    #     pic_7 = ''
                    # if user_data.pic_8:
                    #     pic_8 = user_data.pic_8.url
                    # else:
                    #     pic_8 = ''
                    # if user_data.pic_9:
                    #     pic_9 = user_data.pic_9.url
                    # else:
                    #     pic_9 = ''
                    Data = {
                        "id": user_data.id,
                        "email": user_data.email,
                        "first_name": user_data.first_name,
                        "last_name": user_data.last_name,
                        "phone_number": user_data.phone_number,
                        "gender": user_data.gender,
                        "date_of_birth": user_data.date_of_birth,
                        # "job_profile": user_data.job_profile,
                        # "company_name": user_data.company_name,
                        # "qualification": user_data.qualification,
                        # "relationship_status": user_data.relationship_status,
                        # "interests": user_data.interests,
                        # "fav_quote": user_data.fav_quote,
                        "pic_1": pic_1,
                        "pic_2": pic_2,
                        "pic_3": pic_3,
                        "pic_4": pic_4,
                        "pic_5": pic_5,
                        "pic_6": pic_6,
                        # "pic_7": pic_7,
                        # "pic_8": pic_8,
                        # "pic_9": pic_9,
                        "discovery_lat": user_detail.discovery[0],
                        "discovery_lang": user_detail.discovery[1],
                        "distance_range": user_detail.distance_range,
                        "min_age_range": user_detail.min_age_range,
                        "max_age_range": user_detail.max_age_range,
                        "interested": user_detail.interest,
                        "verified": user_data.verified
                    }
                    r_user = RegisterUser.objects.get(email=user.email)
                    account = DeactivateAccount.objects.get(user=r_user)
                    if account.deactivated:
                        account.deactivated = False
                        account.save()
                        user_detail.deactivated = False
                        user_detail.save()
                    return Response(
                        {"Token": token.key, "user_id": reg_usr.id, 'data': Data, 'deactivated': account.deactivated,
                         "status": HTTP_200_OK})
                else:
                    reg_usr = RegisterUser.objects.create(
                        email=email,
                        first_name=name,
                        date_of_birth=dob,
                        pic_1=profile_pic,
                        verified=True
                    )
                    user = User.objects.create(
                        name=name,
                        # last_name=last_name,
                        email=email,
                        social_id=social_id,
                        social_type=social_type,
                        # profile_pic=profile_pic,
                        device_token=device_token,
                    )
                    UserDetail.objects.create(
                        phone_number=reg_usr,
                        discovery=fromstr(f'POINT({lang} {lat})', srid=4326)
                    )
                    DeactivateAccount.objects.create(
                        user=reg_usr
                    )
                    token = Token.objects.create(user=user)
                    user_data = RegisterUser.objects.get(email=user.email)
                    user_detail = UserDetail.objects.get(phone_number=user_data)
                    pic_1 = ''
                    pic_2 = ''
                    pic_3 = ''
                    pic_4 = ''
                    pic_5 = ''
                    pic_6 = ''
                    pic_7 = ''
                    pic_8 = ''
                    pic_9 = ''
                    if user_data.pic_1:
                        pic_1 = user_data.pic_1.url
                    else:
                        pic_1 = ''
                    if user_data.pic_2:
                        pic_2 = user_data.pic_2.url
                    else:
                        pic_2 = ''
                    if user_data.pic_3:
                        pic_3 = user_data.pic_3.url
                    else:
                        pic_3 = ''
                    if user_data.pic_4:
                        pic_4 = user_data.pic_4.url
                    else:
                        pic_4 = ''
                    if user_data.pic_5:
                        pic_5 = user_data.pic_5.url
                    else:
                        pic_5 = ''
                    if user_data.pic_6:
                        pic_6 = user_data.pic_6.url
                    else:
                        pic_6 = ''
                    # if user_data.pic_7:
                    #     pic_7 = user_data.pic_8.url
                    # else:
                    #     pic_7 = ''
                    # if user_data.pic_8:
                    #     pic_8 = user_data.pic_8.url
                    # else:
                    #     pic_8 = ''
                    # if user_data.pic_9:
                    #     pic_9 = user_data.pic_9.url
                    # else:
                    #     pic_9 = ''
                    Data = {
                        "id": user_data.id,
                        "email": user_data.email,
                        "first_name": user_data.first_name,
                        "last_name": user_data.last_name,
                        "phone_number": user_data.phone_number,
                        "gender": user_data.gender,
                        "date_of_birth": user_data.date_of_birth,
                        # "job_profile": user_data.job_profile,
                        # "company_name": user_data.company_name,
                        # "qualification": user_data.qualification,
                        # "relationship_status": user_data.relationship_status,
                        # "interests": user_data.interests,
                        # "fav_quote": user_data.fav_quote,
                        "pic_1": pic_1,
                        "pic_2": pic_2,
                        "pic_3": pic_3,
                        "pic_4": pic_4,
                        "pic_5": pic_5,
                        "pic_6": pic_6,
                        # "pic_7": pic_7,
                        # "pic_8": pic_8,
                        # "pic_9": pic_9,
                        "discovery_lat": user_detail.discovery[0],
                        "discovery_lang": user_detail.discovery[1],
                        "distance_range": user_detail.distance_range,
                        "min_age_range": user_detail.min_age_range,
                        "max_age_range": user_detail.max_age_range,
                        "interested": user_detail.interest,
                        "verified": user_data.verified
                    }
                    r_user = RegisterUser.objects.get(email=user.email)
                    account = DeactivateAccount.objects.get(user=r_user)
                    if account.deactivated:
                        account.deactivated = False
                        account.save()
                        user_detail.deactivated = False
                        user_detail.save()
                    return Response(
                        {"Token": token.key, "user_id": reg_usr.id, 'data': Data,
                         'deactivated': account.deactivated,
                         "status": HTTP_200_OK})
            else:
                return Response({"message": serializer.errors, "status": HTTP_400_BAD_REQUEST})


class GoogleSignupView(CreateAPIView):
    serializer_class = GmailSerializer

    def post(self, request, *args, **kwargs):
        print(self.request.data)
        # name = self.request.POST.get('name' or None)
        name = self.request.data['name']
        # last_name = self.request.POST.get('last_name' or None)
        # email = self.request.data.POST['email']
        email = self.request.data['email']
        # email = self.request.POST.get('email' or None)
        print('>>>>>>>>>>>>>>', email)
        # social_id = self.request.POST.get('social_id' or None)
        social_id = self.request.data['social_id']
        # social_type = self.request.POST.get('social_type' or None)
        social_type = self.request.data['social_type']
        # device_token = self.request.POST.get('device_token' or None)
        device_token = self.request.data['device_token']
        profile_pic = self.request.POST.get('profile_pic' or None)
        lat = self.request.POST.get('lat' or None)
        lang = self.request.POST.get('lang' or None)
        dob = self.request.POST.get('dob' or None)
        try:
            print('Gmail try---------------->', self.request.data)
            # print('>>>>>>>>>>>>>>', email)
            existing_user = User.objects.get(social_id=social_id)
            if existing_user:
                user_with_token = Token.objects.get_or_create(
                    user=existing_user)
                print('token-->>', user_with_token)
                existing_user.device_token = device_token
                print('from google sign in device token ', device_token)
                existing_user.save(update_fields=['device_token'])
                user_with_token = user_with_token[0]
                print(user_with_token)
                user_data = RegisterUser.objects.get(email=existing_user.email)
                # user_data = RegisterUser.objects.get(email=user.email)
                user_detail = UserDetail.objects.get(phone_number=user_data)
                pic_1 = ''
                pic_2 = ''
                pic_3 = ''
                pic_4 = ''
                pic_5 = ''
                pic_6 = ''
                pic_7 = ''
                pic_8 = ''
                pic_9 = ''
                if user_data.pic_1:
                    pic_1 = user_data.pic_1.url
                else:
                    pic_1 = ''
                if user_data.pic_2:
                    pic_2 = user_data.pic_2.url
                else:
                    pic_2 = ''
                if user_data.pic_3:
                    pic_3 = user_data.pic_3.url
                else:
                    pic_3 = ''
                if user_data.pic_4:
                    pic_4 = user_data.pic_4.url
                else:
                    pic_4 = ''
                if user_data.pic_5:
                    pic_5 = user_data.pic_5.url
                else:
                    pic_5 = ''
                if user_data.pic_6:
                    pic_6 = user_data.pic_6.url
                else:
                    pic_6 = ''
                # if user_data.pic_7:
                #     pic_7 = user_data.pic_8.url
                # else:
                #     pic_7 = ''
                # if user_data.pic_8:
                #     pic_8 = user_data.pic_8.url
                # else:
                #     pic_8 = ''
                # if user_data.pic_9:
                #     pic_9 = user_data.pic_9.url
                # else:
                #     pic_9 = ''
                Data = {
                    "id": user_data.id,
                    "email": user_data.email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "phone_number": user_data.phone_number,
                    "gender": user_data.gender,
                    "date_of_birth": user_data.date_of_birth,
                    # "job_profile": user_data.job_profile,
                    # "company_name": user_data.company_name,
                    # "qualification": user_data.qualification,
                    # "relationship_status": user_data.relationship_status,
                    # "interests": user_data.interests,
                    # "fav_quote": user_data.fav_quote,
                    "pic_1": pic_1,
                    "pic_2": pic_2,
                    "pic_3": pic_3,
                    "pic_4": pic_4,
                    "pic_5": pic_5,
                    "pic_6": pic_6,
                    # "pic_7": pic_7,
                    # "pic_8": pic_8,
                    # "pic_9": pic_9,
                    "discovery_lat": user_detail.discovery[0],
                    "discovery_lang": user_detail.discovery[1],
                    "distance_range": user_detail.distance_range,
                    "min_age_range": user_detail.min_age_range,
                    "max_age_range": user_detail.max_age_range,
                    "interested": user_detail.interest
                }
                r_user = RegisterUser.objects.get(email=existing_user.email)
                account = DeactivateAccount.objects.get(user=r_user)
                if account.deactivated:
                    account.deactivated = False
                    account.save()
                    user_detail.deactivated = False
                    user_detail.save()
                return Response({"Token": user_with_token.key, "user id": user_data.id, 'data': Data,
                                 'deactivated': account.deactivated, "status": HTTP_200_OK})
        except:
            print('Gmail except ----------------->>>>>>>>>>>', self.request.data)
            # print('>>>>>>>>>>>>>>', self.request.data.POST('email'))
            serializer = GmailSerializer(data=request.data)
            if serializer.is_valid():
                if profile_pic is not None and profile_pic != '':
                    pic = ''
                    data = ''
                    image_url = profile_pic
                    img_data = requests.get(image_url).content
                    with open(f'{social_id}.png', 'wb') as handler:
                        handler.write(img_data)
                        pic = handler.name
                    with open(os.path.abspath(pic), 'rb') as f:
                        print('FFFFFFFFFFFFFF_______________', f)
                        data = f.read()
                    reg_usr = RegisterUser.objects.create(
                        email=email,
                        first_name=name,
                        date_of_birth=dob,
                        # pic_1=profile_pic
                    )
                    reg_usr.pic_1.save(f'{social_id}.png', ContentFile(data))
                    print(reg_usr.pic_1.url)
                    user = User.objects.create(
                        name=name,
                        # last_name=last_name,
                        email=email,
                        social_id=social_id,
                        social_type=social_type,
                        device_token=device_token,
                        # profile_pic=profile_pic
                    )
                    UserDetail.objects.create(
                        phone_number=reg_usr,
                        discovery=fromstr(f'POINT({lang} {lat})', srid=4326)
                    )
                    DeactivateAccount.objects.create(
                        user=reg_usr
                    )
                    token = Token.objects.create(user=user)
                    # user_data = RegisterUser.objects.get(email=existing_user.email)
                    user_data = RegisterUser.objects.get(email=user.email)
                    user_detail = UserDetail.objects.get(phone_number=user_data)
                    pic_1 = ''
                    pic_2 = ''
                    pic_3 = ''
                    pic_4 = ''
                    pic_5 = ''
                    pic_6 = ''
                    pic_7 = ''
                    pic_8 = ''
                    pic_9 = ''
                    if user_data.pic_1:
                        pic_1 = user_data.pic_1.url
                    else:
                        pic_1 = ''
                    if user_data.pic_2:
                        pic_2 = user_data.pic_2.url
                    else:
                        pic_2 = ''
                    if user_data.pic_3:
                        pic_3 = user_data.pic_3.url
                    else:
                        pic_3 = ''
                    if user_data.pic_4:
                        pic_4 = user_data.pic_4.url
                    else:
                        pic_4 = ''
                    if user_data.pic_5:
                        pic_5 = user_data.pic_5.url
                    else:
                        pic_5 = ''
                    if user_data.pic_6:
                        pic_6 = user_data.pic_6.url
                    else:
                        pic_6 = ''
                    # if user_data.pic_7:
                    #     pic_7 = user_data.pic_8.url
                    # else:
                    #     pic_7 = ''
                    # if user_data.pic_8:
                    #     pic_8 = user_data.pic_8.url
                    # else:
                    #     pic_8 = ''
                    # if user_data.pic_9:
                    #     pic_9 = user_data.pic_9.url
                    # else:
                    #     pic_9 = ''
                    Data = {
                        "id": user_data.id,
                        "email": user_data.email,
                        "first_name": user_data.first_name,
                        "last_name": user_data.last_name,
                        "phone_number": user_data.phone_number,
                        "gender": user_data.gender,
                        "date_of_birth": user_data.date_of_birth,
                        # "job_profile": user_data.job_profile,
                        # "company_name": user_data.company_name,
                        # "qualification": user_data.qualification,
                        # "relationship_status": user_data.relationship_status,
                        # "interests": user_data.interests,
                        # "fav_quote": user_data.fav_quote,
                        "pic_1": pic_1,
                        "pic_2": pic_2,
                        "pic_3": pic_3,
                        "pic_4": pic_4,
                        "pic_5": pic_5,
                        "pic_6": pic_6,
                        # "pic_7": pic_7,
                        # "pic_8": pic_8,
                        # "pic_9": pic_9,
                        "discovery_lat": user_detail.discovery[0],
                        "discovery_lang": user_detail.discovery[1],
                        "distance_range": user_detail.distance_range,
                        "min_age_range": user_detail.min_age_range,
                        "max_age_range": user_detail.max_age_range,
                        "interested": user_detail.interest
                    }
                    existing_user = User.objects.get(social_id=social_id)
                    r_user = RegisterUser.objects.get(email=existing_user.email)
                    account = DeactivateAccount.objects.get(user=r_user)
                    if account.deactivated:
                        account.deactivated = False
                        account.save()
                        user_detail.deactivated = False
                        user_detail.save()
                    return Response({"Token": token.key, "user_id": reg_usr.id, 'data': Data,
                                     'deactivated': account.deactivated, "status": HTTP_200_OK})
                else:
                    reg_usr = RegisterUser.objects.create(
                        email=email,
                        first_name=name,
                        date_of_birth=dob,
                        # pic_1=profile_pic
                    )
                    reg_usr.pic_1.save(f'{social_id}.png', ContentFile(data))
                    print(reg_usr.pic_1.url)
                    user = User.objects.create(
                        name=name,
                        # last_name=last_name,
                        email=email,
                        social_id=social_id,
                        social_type=social_type,
                        device_token=device_token,
                        # profile_pic=profile_pic
                    )
                    UserDetail.objects.create(
                        phone_number=reg_usr,
                        discovery=fromstr(f'POINT({lang} {lat})', srid=4326)
                    )
                    DeactivateAccount.objects.create(
                        user=reg_usr
                    )
                    token = Token.objects.create(user=user)
                    # user_data = RegisterUser.objects.get(email=existing_user.email)
                    user_data = RegisterUser.objects.get(email=user.email)
                    user_detail = UserDetail.objects.get(phone_number=user_data)
                    pic_1 = ''
                    pic_2 = ''
                    pic_3 = ''
                    pic_4 = ''
                    pic_5 = ''
                    pic_6 = ''
                    pic_7 = ''
                    pic_8 = ''
                    pic_9 = ''
                    if user_data.pic_1:
                        pic_1 = user_data.pic_1.url
                    else:
                        pic_1 = ''
                    if user_data.pic_2:
                        pic_2 = user_data.pic_2.url
                    else:
                        pic_2 = ''
                    if user_data.pic_3:
                        pic_3 = user_data.pic_3.url
                    else:
                        pic_3 = ''
                    if user_data.pic_4:
                        pic_4 = user_data.pic_4.url
                    else:
                        pic_4 = ''
                    if user_data.pic_5:
                        pic_5 = user_data.pic_5.url
                    else:
                        pic_5 = ''
                    if user_data.pic_6:
                        pic_6 = user_data.pic_6.url
                    else:
                        pic_6 = ''
                    # if user_data.pic_7:
                    #     pic_7 = user_data.pic_8.url
                    # else:
                    #     pic_7 = ''
                    # if user_data.pic_8:
                    #     pic_8 = user_data.pic_8.url
                    # else:
                    #     pic_8 = ''
                    # if user_data.pic_9:
                    #     pic_9 = user_data.pic_9.url
                    # else:
                    #     pic_9 = ''
                    Data = {
                        "id": user_data.id,
                        "email": user_data.email,
                        "first_name": user_data.first_name,
                        "last_name": user_data.last_name,
                        "phone_number": user_data.phone_number,
                        "gender": user_data.gender,
                        "date_of_birth": user_data.date_of_birth,
                        # "job_profile": user_data.job_profile,
                        # "company_name": user_data.company_name,
                        # "qualification": user_data.qualification,
                        # "relationship_status": user_data.relationship_status,
                        # "interests": user_data.interests,
                        # "fav_quote": user_data.fav_quote,
                        "pic_1": pic_1,
                        "pic_2": pic_2,
                        "pic_3": pic_3,
                        "pic_4": pic_4,
                        "pic_5": pic_5,
                        "pic_6": pic_6,
                        # "pic_7": pic_7,
                        # "pic_8": pic_8,
                        # "pic_9": pic_9,
                        "discovery_lat": user_detail.discovery[0],
                        "discovery_lang": user_detail.discovery[1],
                        "distance_range": user_detail.distance_range,
                        "min_age_range": user_detail.min_age_range,
                        "max_age_range": user_detail.max_age_range,
                        "interested": user_detail.interest
                    }
                    existing_user = User.objects.get(social_id=social_id)
                    r_user = RegisterUser.objects.get(email=existing_user.email)
                    account = DeactivateAccount.objects.get(user=r_user)
                    if account.deactivated:
                        account.deactivated = False
                        account.save()
                        user_detail.deactivated = False
                        user_detail.save()
                    return Response({"Token": token.key, "user_id": reg_usr.id, 'data': Data,
                                     'deactivated': account.deactivated, "status": HTTP_200_OK})
            else:
                return Response({"message": serializer.errors, "status": HTTP_400_BAD_REQUEST})


class CheckNumber(APIView):
    model = User

    def post(self, request, *args, **kwargs):
        # phone_number = self.request.GET.get('phone_number')
        phone_number = self.request.POST['phone_number']
        # print('<<<<<<<<<<<<<<<<<<<<<<<<<<<',phone_number)
        # user = User.objects.get(phone_number=phone_number)
        # app_user = RegisterUser.objects.get(phone_number=phone_number)
        # print('>>>>>>>>>>>>>>>>', user)
        # print('<<<<<<<<<<<', app_user)
        try:
            user = User.objects.get(phone_number=phone_number)
            app_user = RegisterUser.objects.get(phone_number=phone_number)
            print('>>>>>>>>>>>>>>>>', user)
            print('<<<<<<<<<<<', app_user)
            if user or app_user:
                return Response(
                    {'message': 'User already registered with this number', 'user_exists': True,
                     "status": HTTP_200_OK})
            else:
                return Response({'message': 'User not found', 'user_exists': False, "status": HTTP_400_BAD_REQUEST})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'user_exists': False, "status": HTTP_400_BAD_REQUEST})


class GetNotificationList(APIView):
    model = UserNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        notifications = UserNotification.objects.filter(to=user)
        return Response({"data": notifications.values(), "status": HTTP_200_OK})


class UpdateNotification(APIView):
    model = UserNotification
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = UserNotification.objects.all()

    def get(self, request, *args, **kwargs):
        # serializer = NotificationSerializer(data=request.data)
        # instance = self.get_object()
        # instance.read = True
        # if serializer.is_valid():
        #     instance.save(update_fields=['read'])
        user = self.request.user
        # user = User.objects.get(to=user.id)
        notifications = UserNotification.objects.filter(
            to=user.id).filter(read=False)
        for obj in notifications:
            obj.read = True
            obj.save()
        return Response({"message": "Notification read successfully", "status": HTTP_200_OK})


class DeleteNotification(APIView):
    model = UserNotification
    # serializer_class = NotificationSerializer
    queryset = UserNotification.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        id = self.request.data['id']
        try:
            obj = UserNotification.objects.get(id=id)
            obj.delete()
            return Response({"message": "Notification deleted successfully", "status": HTTP_200_OK})
        except Exception as e:
            print(e)
            return Response(
                {"message": "Notification with this id does not exists", "status": HTTP_400_BAD_REQUEST})


class UpdateInterest(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = RegisterUser.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        user_obj = RegisterUser.objects.get(email=user.email)
        user_detail = UserDetail.objects.get(phone_number=user_obj)
        user_detail.interest = request.data.get('interest')
        user_detail.save()
        return Response({"message": "Your interest has been updated", "status": HTTP_200_OK})


class GetUnreadMessageCount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        count = UserNotification.objects.filter(to=user.id).filter(read=False).count()
        print(count)
        return Response({"count": count, "status": HTTP_200_OK})


class UpdateDistanceRange(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        distance_range = self.request.POST['distance_range']
        r_user = RegisterUser.objects.get(email=user.email)
        user_detail_obj = UserDetail.objects.get(phone_number=r_user)
        user_detail_obj.distance_range = distance_range
        user_detail_obj.save()
        return Response({'message': 'Distance range updated successfully', 'status': HTTP_200_OK})


class UpdateAgeRange(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        min_age = self.request.POST['min_age']
        max_age = self.request.POST['max_age']
        r_user = RegisterUser.objects.get(email=user.email)
        user_detail_obj = UserDetail.objects.get(phone_number=r_user)
        user_detail_obj.min_age_range = min_age
        user_detail_obj.max_age_range = max_age
        user_detail_obj.save()
        return Response({'message': 'Updated age range successfully', 'status': HTTP_200_OK})


class DeleteAccount(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        request.user.auth_token.delete()
        user.delete()
        r_user = RegisterUser.objects.get(email=user.email)
        r_user.delete()
        return Response({'message': 'Account deleted successfully', 'status': HTTP_200_OK})


class DeactivateAccountView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    models = DeactivateAccount

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        user_detail = UserDetail.objects.get(phone_number=r_user)
        account = DeactivateAccount.objects.get(user=r_user)
        if account.deactivated:
            account.deactivated = False
            account.save()
            user_detail.deactivated = False
            user_detail.save()
            return Response({'message': 'Account activated successfully', 'deactivated': account.deactivated,
                             'status': HTTP_200_OK})
        else:
            account.deactivated = True
            account.save()
            user_detail.deactivated = True
            user_detail.save()
            return Response({'message': 'Account deactivated successfully', 'deactivated': account.deactivated,
                             'status': HTTP_200_OK})


class CheckMeeting(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ScheduleMeeting

    def get(self, request, *args, **kwargs):
        user1 = self.request.query_params.get('user1')
        user2 = self.request.query_params.get('user2')
        try:
            try:
                meeting = ScheduleMeeting.objects.filter(scheduled_with=user1, scheduled_by=user2).exclude(
                    status='Rejected')
                meeting_2 = ScheduleMeeting.objects.filter(scheduled_with=user2, scheduled_by=user1).exclude(
                    status='Rejected')
                print('meetings inside try', meeting, meeting_2)
                if len(meeting) > 0 or len(meeting_2) > 0:
                    return Response({'meeting_exists': True, 'meeting_id': meeting.first().id, 'status': HTTP_200_OK})
                else:
                    return Response({'meeting_exists': False, 'meeting_id': '', 'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                print('Exception', e)
                meeting = ScheduleMeeting.objects.filter(scheduled_with=user2, scheduled_by=user1).exclude(
                    status='Rejected')
                meeting_2 = ScheduleMeeting.objects.filter(scheduled_with=user1, scheduled_by=user2).exclude(
                    status='Rejected')
                print('meetings inside except', meeting, meeting_2)
                if len(meeting) > 0 or len(meeting_2) > 0:
                    return Response({'meeting_exists': True, 'meeting_id': meeting.first().id, 'status': HTTP_200_OK})
                else:
                    return Response({'meeting_exists': False, 'meeting_id': '', 'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            return Response({'meeting_exists': False, 'status': HTTP_400_BAD_REQUEST})


class UnMatchView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            match_id = self.request.POST['match_id']
            match = MatchedUser.objects.get(id=match_id)
            match.delete()
            return Response({'message': 'Unmatched successfully', 'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})


class BlockUserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = BlockedUsers

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST['id']
        try:
            r_user = RegisterUser.objects.get(email=self.request.user.email)
            print('inside try')
            print('user_id')
            blocked_user_obj = BlockedUsers.objects.get(user=r_user)
            if blocked_user_obj:
                blocked_user_obj.blocked.add(RegisterUser.objects.get(id=int(user_id)))
                return Response({'message': 'User blocked successfully', 'status': HTTP_200_OK})
        except Exception as e:
            print('Inside exception', e)
            # x = {'error': str(e)}
            block = BlockedUsers.objects.create(
                user=RegisterUser.objects.get(email=self.request.user.email),
                # blocked=RegisterUser.objects.get(id=int(user_id))
            )
            block.blocked.add(RegisterUser.objects.get(id=int(user_id)))
            return Response({'message': 'User blocked successfully', 'status': HTTP_200_OK})


class BlockedUsersList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = BlockedUsers

    def get(self, request, *args, **kwargs):
        try:
            blocked_users_list = []
            r_user = RegisterUser.objects.get(email=self.request.user.email)
            blocked_users = BlockedUsers.objects.get(user=r_user)
            for x in blocked_users.blocked.all():
                if RegisterUser.objects.get(id=x.id).pic_1:
                    blocked_users_list.append({'id': x.id, 'first_name': RegisterUser.objects.get(id=x.id).first_name,
                                               'last_name': RegisterUser.objects.get(id=x.id).last_name,
                                               'profile_pic': RegisterUser.objects.get(id=x.id).pic_1.url})
                else:
                    blocked_users_list.append({'id': x.id, 'first_name': RegisterUser.objects.get(id=x.id).first_name,
                                               'last_name': RegisterUser.objects.get(id=x.id).last_name,
                                               'profile_pic': ''})
            return Response({'data': blocked_users_list, 'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})


class UnBlockUser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = BlockedUsers

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST['id']
        try:
            r_user = RegisterUser.objects.get(email=self.request.user.email)
            print('inside try')
            print('user_id')
            blocked_user_obj = BlockedUsers.objects.filter(user=r_user)
            if blocked_user_obj:
                for obj in blocked_user_obj:
                    for x in obj.blocked.all():
                        if x.id == int(user_id):
                            obj.blocked.remove(RegisterUser.objects.get(id=int(user_id)))
                return Response({'message': 'User unblocked successfully', 'status': HTTP_200_OK})
        except Exception as e:
            print('Inside exception', e)
            x = {'error': str(e)}
            return Response({'message': x['error'], 'status': HTTP_200_OK})


class CheckEmail(APIView):

    def post(self, request, *args, **kwargs):
        email = self.request.POST['email']
        try:
            user = User.objects.get(email=email)
            return Response({'message': 'User with this email already exists', 'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'status': HTTP_200_OK})


class CheckUserBlocked(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user1 = self.request.POST['user1']
        user2 = self.request.POST['user2']
        user_1_blocked_list = []
        user_2_blocked_list = []
        try:
            blocked_users_1 = BlockedUsers.objects.get(user=RegisterUser.objects.get(id=user1))
            blocked_users_2 = BlockedUsers.objects.get(user=RegisterUser.objects.get(id=user2))
            for user in blocked_users_1.blocked.all():
                # for x in user.blocked.all():
                user_1_blocked_list.append(user.id)
            for user in blocked_users_2.blocked.all():
                # for x in user.blocked.all():
                user_2_blocked_list.append(user.id)
            blocked_users_list = user_1_blocked_list + user_2_blocked_list
            print('blocked users list', blocked_users_list)
            if int(user1) in blocked_users_list or int(user2) in blocked_users_list:
                return Response({'blocked': True, 'status': HTTP_200_OK})
            else:
                return Response({'blocked': False, 'status': HTTP_200_OK})
        except:
            return Response({'blocked': False, 'status': HTTP_200_OK})


class PopNotificationAPIView(CreateAPIView):
    serializer_class = PopUpNotificationSerializer

    def post(self, request, *args, **kwargs):
        return Response({"You have updated your meeting status successfully"}, status=HTTP_200_OK)


class SubscriptionPlanAPIView(ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlans.objects.all()


class GetMediaContent(APIView):
    def get(self, request, *args, **kwargs):
        # os.path.isdir("media")
        # os.chdir("media")
        for path, dirs, files in os.walk("media"):
            for filename in files:
                print(os.path.join(path, filename))
        for f in os.listdir("media"):
            print('------>>>')
            print(f)
            return Response({"sdgfsgjas"})


class UserAge(APIView):
    def get(self, request, *args, **kwargs):
        user = RegisterUser.objects.all()[0]
        age = timezone.now().date().year - user.date_of_birth.year
        print('date ', timezone.now().date())
        print('Date of birth ', user.date_of_birth)
        return Response({'age': age})


class FCMNotification(APIView):

    def get(self, request, *args, **kwargs):
        FCMDevice.objects.create(
            name='Test',
            user=User.objects.all().first(),
            device_id='enbaCq8MQF-dPIFfF-ifFH:APA91bEhGKw43G1YcoMGJQZ2rRGhfneKwaMsX1OX68JKkiLOPz1NLJ_BqIW0ttpiszepwIMIR4liWbGCdsYa_Rv-Ft2PIaxtqFEg7ND7L5Mzlu92KHOqk0gyyIWhp7kQhVyPh0FMn_fc',
            # registration_token='AAAAORwXGTc:APA91bFzV3R5Agp3wnrvhYwGbA4n-v5x-sBF9_nAgwPv6HVl92RyNontEw0A8RzNOQvVTOOKvKzpU_XrFFg--uAvkazmFfL03X71XjUe8CEZiLUmLtVfho4jtDVXdmm6rrfPkOqdroP6',
            type='android'
        )
        device = FCMDevice.objects.all().first()
        x = device.send_message(title="Title", body="Message", icon=..., data={"test": "test"})
        print(x)
        return 'Sent Push Notification'


class MeetupPopUs(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        meetings_scheduled_by_me = ScheduleMeeting.objects.filter(scheduled_by=r_user)
        meetings_scheduled_with_me = ScheduleMeeting.objects.filter(scheduled_with=r_user)
        meetings = []
        print('Meetings scheduled by me----->>', meetings_scheduled_by_me)
        print('Meetins scheduled with me ------>>>', meetings_scheduled_with_me)
        print('Both Meeting----------', meetings_scheduled_by_me | meetings_scheduled_with_me)
        for meeting in meetings_scheduled_by_me | meetings_scheduled_with_me:
            print('Meeting date and time---->>', str(meeting.meeting_date) + str(meeting.meeting_time))
            # print(meeting.meeting_date + meeting.meeting_time)
            print('Timezone------>>>', timezone.now().replace(microsecond=0))
            import datetime
            print('>>>>>>>>>>>',
                  datetime.datetime.combine(meeting.meeting_date, meeting.meeting_time) + timedelta(hours=24))
            print(timezone.now().replace(microsecond=0) > datetime.datetime.combine(meeting.meeting_date,
                                                                                    meeting.meeting_time) + timedelta(
                hours=24))
            if meeting.status.lower() == 'accepted' and timezone.now().replace(
                    microsecond=0) > datetime.datetime.combine(meeting.meeting_date,
                                                               meeting.meeting_time) + timedelta(hours=24):
                print('inside if ')
                print(meeting)
                print(meeting.id)
                if meeting.status_update_count > 0:
                    pass
                else:
                    meeting.status_update_count += 1
                    meeting.save()
                    meetings.append({'meeting_id': meeting.id, 'scheduled_by_id': meeting.scheduled_by.id,
                                     'scheduled_by': meeting.scheduled_by.first_name,
                                     'scheduled_with_id': meeting.scheduled_with.id,
                                     'scheduled_with': meeting.scheduled_with.first_name})
            else:
                print('else case')
                pass
        return Response({'data': meetings, 'status': HTTP_200_OK})


class MeetupStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        meeting_id = self.request.POST['meeting_id']
        user1 = self.request.POST['user1']
        user2 = self.request.POST['user2']
        status = self.request.POST['status']
        try:
            x = PopNotification.objects.get(user1=user1, user2=user2, meeting=meeting_id)
            return Response({'data': x.status, 'status': HTTP_200_OK})
        except Exception as e:
            try:
                x = PopNotification.objects.get(user1=user2, user2=user1, meeting=meeting_id)
                return Response({'data': x.status, 'status': HTTP_200_OK})
            except Exception as e:
                try:
                    meeting_obj = ScheduleMeeting.objects.get(id=meeting_id)
                    x = PopNotification.objects.create(user1=RegisterUser.objects.get(id=user1),
                                                       user2=RegisterUser.objects.get(id=user2),
                                                       meeting=meeting_obj, status=status)
                except Exception as e:
                    x = {'error': str(e)}
                    return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})
                return Response({'data': x.status, 'status': HTTP_200_OK})


class DisconnectWithInstagram(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        id = self.request.POST['user_id']
        print('iD------------', id)
        user = self.request.user
        try:
            r_user = RegisterUser.objects.get(id=id)
            print(r_user)
            pics = UserInstagramPic.objects.filter(phone_number=r_user).last()
            pics.delete()
            # r_user.verified = False
            # r_user.save()
            return Response({'message': 'Disconnected instagram successfully', 'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})


class ClearNotification(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserNotification

    def get(self, request, *args, **kwargs):
        # r_user = RegisterUser.objects.get(email=self.request.user.email)
        notifications = UserNotification.objects.filter(to=self.request.user)
        for notification in notifications:
            notification.delete()
        return Response({"message": "Notifications cleared successfully", 'status': HTTP_200_OK})


class CheckUserProfileCompleteStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print(r_user.id)
        user_detail_obj = UserDetail.objects.get(phone_number=r_user)
        print(user_detail_obj.id)
        pic_1 = ''
        pic_2 = ''
        pic_3 = ''
        pic_4 = ''
        pic_5 = ''
        pic_6 = ''
        if user_detail_obj.phone_number.pic_1:
            pic_1 = user_detail_obj.phone_number.pic_1.url
        else:
            pic_1 = ''
        if user_detail_obj.phone_number.pic_2:
            pic_2 = user_detail_obj.phone_number.pic_2.url
        else:
            pic_2 = ''
        if user_detail_obj.phone_number.pic_3:
            pic_3 = user_detail_obj.phone_number.pic_3.url
        else:
            pic_3 = ''
        if user_detail_obj.phone_number.pic_4:
            pic_4 = user_detail_obj.phone_number.pic_4.url
        else:
            pic_4 = ''
        if user_detail_obj.phone_number.pic_5:
            pic_5 = user_detail_obj.phone_number.pic_5.url
        else:
            pic_5 = ''
        if user_detail_obj.phone_number.pic_6:
            pic_6 = user_detail_obj.phone_number.pic_6.url
        else:
            pic_6 = ''
        id = user_detail_obj.phone_number.id
        bio = user_detail_obj.bio
        first_name = user_detail_obj.phone_number.first_name
        last_name = user_detail_obj.phone_number.last_name
        email = user_detail_obj.phone_number.email
        gender = user_detail_obj.phone_number.gender
        date_of_birth = user_detail_obj.phone_number.date_of_birth
        job_profile = user_detail_obj.phone_number.job_profile
        company_name = user_detail_obj.phone_number.company_name
        qualification = user_detail_obj.phone_number.qualification
        relationship_status = user_detail_obj.phone_number.relationship_status
        height = user_detail_obj.phone_number.height
        zodiac_sign = user_detail_obj.phone_number.zodiac_sign
        fav_quote = user_detail_obj.phone_number.fav_quote
        religion = user_detail_obj.phone_number.religion
        body_type = user_detail_obj.phone_number.body_type
        verified = user_detail_obj.phone_number.verified
        fb_signup = user_detail_obj.phone_number.fb_signup
        pic_1 = pic_1
        pic_2 = pic_2
        pic_3 = pic_3
        pic_4 = pic_4
        pic_5 = pic_5
        pic_6 = pic_6
        living_in = user_detail_obj.living_in
        hometown = user_detail_obj.hometown
        profession = user_detail_obj.profession
        college_name = user_detail_obj.college_name
        university = user_detail_obj.university
        personality = user_detail_obj.personality
        preference_first_date = user_detail_obj.preference_first_date
        fav_music = user_detail_obj.fav_music
        interest = user_detail_obj.interest
        food_type = user_detail_obj.food_type
        owns = user_detail_obj.owns
        travelled_place = user_detail_obj.travelled_place
        once_in_life = user_detail_obj.once_in_life
        exercise = user_detail_obj.exercise
        looking_for = user_detail_obj.looking_for
        fav_food = user_detail_obj.fav_food
        fav_pet = user_detail_obj.fav_pet
        smoke = user_detail_obj.smoke
        drink = user_detail_obj.drink
        discovery_lat = user_detail_obj.discovery[0]
        discovery_lang = user_detail_obj.discovery[1]
        distance_range = user_detail_obj.distance_range
        min_age_range = user_detail_obj.min_age_range
        max_age_range = user_detail_obj.max_age_range
        if pic_1 == "" or pic_2 == "" or pic_3 == "" or pic_4 == "" or pic_5 == "" or pic_6 == "" or living_in == "" or hometown == "" or profession == "" or college_name == "" or university == "" or personality == "" or preference_first_date == "" or fav_music == "" or interest == "" or food_type == "" or owns == "" or travelled_place == "" or once_in_life == "" or exercise == "" or looking_for == "" or fav_food == "" or fav_pet == "" or smoke == "" or drink == "" or bio == "" or first_name == "" or last_name == "" or email == "" or gender == "" or date_of_birth == "" or job_profile == "" or company_name == "" or qualification == "" or relationship_status == "" or height == "" or zodiac_sign == "" or fav_quote == "" or religion == "" or body_type == "":
            return Response(
                {'message': 'Profile not complete', 'profile_complete_status': False, 'status': HTTP_400_BAD_REQUEST})
        else:
            return Response({'message': 'Profile complete', 'profile_complete_status': True, 'status': HTTP_200_OK})


class ShowProfileToOnlyLikedUsers(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print('>>>>>', r_user.show_only_to_liked)
        if r_user.show_only_to_liked:
            r_user.show_only_to_liked = False
            r_user.save()
        else:
            r_user.show_only_to_liked = True
            r_user.save()
        print('<<<<<<', r_user.show_only_to_liked)
        return Response({'message': 'Setting updated successfully', 'status': HTTP_200_OK})


class GetShowProfileToOnlyLikedUsers(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        return Response(
            {'message': 'Setting fetched successfully', 'value': r_user.show_only_to_liked, 'status': HTTP_200_OK})


class UpdateLookingFor(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        looking_for = self.request.POST['looking_for']
        user = self.request.user
        register_user = RegisterUser.objects.get(email=user.email)
        user_detail_obj = UserDetail.objects.get(phone_number=register_user)
        user_detail_obj.looking_for = looking_for
        user_detail_obj.save()
        return Response({'message': 'Looking for update successfully', 'status': HTTP_200_OK})


class TransactionDataView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Transaction

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        plan_type = self.request.POST['plan_type']
        order_id = self.request.POST['order_id']
        purchase_token = self.request.POST['purchase_token']
        package_name = self.request.POST['package_name']
        duration = self.request.POST['duration']
        amount = self.request.POST['amount']
        auto_renewing = self.request.POST['auto_renewing']
        order_date = self.request.POST['order_date']
        signature = self.request.POST['signature']
        Transaction.objects.create(
            user=r_user,
            plan_type=plan_type,
            order_id=order_id,
            purchase_token=purchase_token,
            package_name=package_name,
            duration=duration,
            amount=amount,
            auto_renewing=auto_renewing,
            order_date=order_date,
            signature=signature
        )
        if plan_type == 'Star' or plan_type == 'star' or plan_type == 'Star':
            UserHeartBeatsPerDay.objects.create(
                user=r_user,
                number_of_heart_beats=5
            )
        return Response({'message': 'Transaction data inserted successfully', 'status': HTTP_200_OK})


class ExtraHeartBeatsView(APIView):
    model = ExtraHeartBeats
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print(ExtraHeartBeats.objects.filter(user=r_user))
        extra_heartbeats = self.request.POST['extra_heartbeats']
        order_id = self.request.POST['order_id']
        purchase_token = self.request.POST['purchase_token']
        package_name = self.request.POST['package_name']
        duration = self.request.POST['duration']
        amount = self.request.POST['amount']
        auto_renewing = self.request.POST['auto_renewing']
        order_date = self.request.POST['order_date']
        signature = self.request.POST['signature']
        try:
            extra_heartbeat_obj = ExtraHeartBeats.objects.get(user=r_user)
            print(extra_heartbeat_obj)
            extra_heartbeat_obj.extra_heartbeats += int(extra_heartbeats)
            extra_heartbeat_obj.save()
            Transaction.objects.create(
                user=r_user,
                # plan_type=plan_type,
                order_id=order_id,
                purchase_token=purchase_token,
                package_name=package_name,
                duration=duration,
                amount=amount,
                auto_renewing=auto_renewing,
                order_date=order_date,
                signature=signature
            )
        except Exception as e:
            print(e)
            ExtraHeartBeats.objects.create(user=r_user, extra_heartbeats=extra_heartbeats)
            Transaction.objects.create(
                user=r_user,
                # plan_type=plan_type,
                order_id=order_id,
                purchase_token=purchase_token,
                package_name=package_name,
                duration=duration,
                amount=amount,
                auto_renewing=auto_renewing,
                order_date=order_date,
                signature=signature
            )
        return Response({'message': 'Transaction successful', 'status': HTTP_200_OK})


class GetAwsCred(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(
            {'ACCESS_KEY_ID': 'AKIAYC6UDNTP4JZJHA6C', 'SECRET_KEY_ID': 'Nr5QCRn6Ne8uKEPxi3VpNaKrbF4cObIjqSy70qEH',
             'status': HTTP_200_OK})


class SubscriptionBasedSuperLike(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print(r_user.id)
        print(UserHeartBeatsPerDay.objects.filter(user=r_user))
        print(ExtraHeartBeats.objects.filter(user=r_user))
        users_liked_by_me = MatchedUser.objects.filter(user=r_user)
        users_liked_me = MatchedUser.objects.filter(super_liked_by_me=r_user)
        super_liked_by_me = self.request.data['super_liked_by_me']
        users_liked_by_me_list = []
        users_liked_me_list = []
        for x in users_liked_me:
            if x.super_liked_by_me.all():
                print('Many to Many field ', x.super_liked_by_me.all()[0].id)
                print('LIKED BY USER', x.user.id)
                users_liked_me_list.append(x.user.id)
        for x in users_liked_by_me:
            if x.super_liked_by_me.all():
                users_liked_by_me_list.append(x.super_liked_by_me.all()[0].id)
        print('USERS LIKED BY ME LIST ', users_liked_by_me_list)
        print('USERS LIKED ME LIST', users_liked_me_list)
        print(super_liked_by_me)
        print(type(super_liked_by_me))
        print(users_liked_me_list + users_liked_by_me_list)
        print(int(super_liked_by_me) in users_liked_me_list + users_liked_by_me_list)
        try:
            print('inside first try block--->>>')
            print(UserHeartBeatsPerDay.objects.filter(user=r_user))
            user_heartbeats = UserHeartBeatsPerDay.objects.filter(user=r_user).last()
            # print('user_heartbeats.number_of_heart_beats---', user_heartbeats)
            print('user_heartbeats.number_of_heart_beats---', user_heartbeats.number_of_heart_beats > 0)
            if user_heartbeats.number_of_heart_beats > 0:
                print('inside try if block')
                print('user_heartbeats.number_of_heart_beats---', user_heartbeats.number_of_heart_beats)
                if int(super_liked_by_me) not in users_liked_by_me_list + users_liked_me_list:
                    register_user = RegisterUser.objects.get(id=r_user.id)
                    from_user_name = register_user.first_name
                    user = MatchedUser.objects.create(user=register_user, super_matched='No')
                    user.super_liked_by_me.add(RegisterUser.objects.get(id=int(super_liked_by_me)))
                    print('Left number_of_heart_beats---', user_heartbeats.number_of_heart_beats)
                    user_heartbeats.number_of_heart_beats -= 1
                    user_heartbeats.save()
                    print('---Left number_of_heart_beats---', user_heartbeats.number_of_heart_beats)
                    to_user_id = RegisterUser.objects.get(id=int(super_liked_by_me))
                    UserNotification.objects.create(
                        to=User.objects.get(email=to_user_id.email),
                        title='Super Match Notification',
                        body="You have been super liked by " + from_user_name,
                        extra_text=f'{register_user.id}'
                    )
                    fcm_token = User.objects.get(email=to_user_id.email).device_token
                    try:
                        title = "Super Like Notification"
                        body = "You have been super liked by " + from_user_name
                        message_type = "superLike"
                        respo = send_another(fcm_token, title, body)
                        print("FCM Response===============>0", respo)
                    except Exception as e:
                        pass
                    return Response({"message": "You have super liked a user", "status": HTTP_200_OK})
                else:
                    try:
                        print('inside sencond try block')
                        try:
                            print('inside third try block')
                            m = MatchedUser.objects.get(user=r_user, super_matched='Yes',
                                                        super_liked_by_me=int(super_liked_by_me))
                            print(m.id)
                            print(m.super_matched)
                            return Response(
                                {'message': 'You have already super matched with this user', 'status': HTTP_200_OK})
                        except Exception as e:
                            m = MatchedUser.objects.get(user=r_user, super_liked_by_me=int(super_liked_by_me))
                            print('--', m.id)
                            print(m.super_matched)
                            return Response(
                                {'message': 'You have already super liked this user', 'status': HTTP_200_OK})
                    except Exception as e:
                        print(e)
                        register_user = RegisterUser.objects.get(id=r_user.id)
                        from_user_name = register_user.first_name
                        user = MatchedUser.objects.create(user=register_user, super_matched='Yes')
                        user.super_liked_by_me.add(RegisterUser.objects.get(id=int(super_liked_by_me)))
                        print('<<<<<<<---Left number_of_heart_beats---', user_heartbeats.number_of_heart_beats)
                        user_heartbeats.number_of_heart_beats -= 1
                        user_heartbeats.save()
                        print('Left number_of_heart_beats--->>>>', user_heartbeats.number_of_heart_beats)
                        to_user_id = RegisterUser.objects.get(id=int(super_liked_by_me))
                        # to_user_name = to_user_id.first_name
                        UserNotification.objects.create(
                            to=User.objects.get(email=to_user_id.email),
                            title='Super Match Notification',
                            body="You have been super matched by " + from_user_name,
                            extra_text=f'{register_user.id}'
                        )
                        fcm_token = User.objects.get(email=to_user_id.email).device_token
                        try:
                            title = "Super Like Notification"
                            body = "You have been super matched with " + from_user_name
                            message_type = "superMatch"
                            respo = send_another(fcm_token, title, body)
                            print("FCM Response===============>0", respo)
                        except Exception as e:
                            pass
                        return Response({"message": "You have super matched with a user", "status": HTTP_200_OK})
            else:
                try:
                    print('inside extra heartbeat try case')
                    extra_heartbeat = ExtraHeartBeats.objects.filter(user=r_user).last()
                    print('---', extra_heartbeat.extra_heartbeats > 0)
                    if extra_heartbeat.extra_heartbeats > 0:
                        print('>>>>>>>>>>>')
                        if int(super_liked_by_me) not in users_liked_by_me_list + users_liked_me_list:
                            register_user = RegisterUser.objects.get(id=r_user.id)
                            from_user_name = register_user.first_name
                            user = MatchedUser.objects.create(user=register_user, super_matched='No')
                            user.super_liked_by_me.add(RegisterUser.objects.get(id=int(super_liked_by_me)))
                            extra_heartbeat.extra_heartbeats -= 1
                            extra_heartbeat.save()
                            to_user_id = RegisterUser.objects.get(id=int(super_liked_by_me))
                            UserNotification.objects.create(
                                to=User.objects.get(email=to_user_id.email),
                                title='Super Match Notification',
                                body="You have been super liked by " + from_user_name,
                                extra_text=f'{register_user.id}'
                            )
                            fcm_token = User.objects.get(email=to_user_id.email).device_token
                            try:
                                title = "Super Like Notification"
                                body = "You have been super liked by " + from_user_name
                                message_type = "superLike"
                                respo = send_another(fcm_token, title, body)
                                print("FCM Response===============>0", respo)
                            except Exception as e:
                                pass
                            return Response({"message": "You have super liked a user", "status": HTTP_200_OK})
                        else:
                            try:
                                try:
                                    m = MatchedUser.objects.get(user=r_user, super_matched='Yes',
                                                                super_liked_by_me=int(super_liked_by_me))
                                    print(m.id)
                                    print(m.super_matched)
                                    return Response(
                                        {'message': 'You have already super matched with this user',
                                         'status': HTTP_200_OK})
                                except Exception as e:
                                    m = MatchedUser.objects.get(user=r_user, super_liked_by_me=int(super_liked_by_me))
                                    print('--', m.id)
                                    print(m.super_matched)
                                    return Response(
                                        {'message': 'You have already super liked this user', 'status': HTTP_200_OK})
                            except Exception as e:
                                print(e)
                                register_user = RegisterUser.objects.get(id=r_user.id)
                                from_user_name = register_user.first_name
                                user = MatchedUser.objects.create(user=register_user, super_matched='Yes')
                                user.super_liked_by_me.add(RegisterUser.objects.get(id=int(super_liked_by_me)))
                                extra_heartbeat.extra_heartbeats -= 1
                                extra_heartbeat.save()
                                to_user_id = RegisterUser.objects.get(id=int(super_liked_by_me))
                                # to_user_name = to_user_id.first_name
                                UserNotification.objects.create(
                                    to=User.objects.get(email=to_user_id.email),
                                    title='Super Match Notification',
                                    body="You have been super matched by " + from_user_name,
                                    extra_text=f'{register_user.id}'
                                )
                                fcm_token = User.objects.get(email=to_user_id.email).device_token
                                try:
                                    title = "Super Like Notification"
                                    body = "You have been super matched with " + from_user_name
                                    message_type = "superMatch"
                                    respo = send_another(fcm_token, title, body)
                                    print("FCM Response===============>0", respo)
                                except Exception as e:
                                    pass
                                return Response(
                                    {"message": "You have super matched with a user", "status": HTTP_200_OK})
                    else:
                        return Response({
                            'message': 'You have run out of superlikes. Please wait till tomorrow or buy extra '
                                       'superlikes',
                            'status': HTTP_400_BAD_REQUEST})
                except Exception as e:
                    print('', e)
                    return Response(
                        {'message': str(e),
                         'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            print('Outer most exception--->>>', e)
            return Response({'message': 'You do not have an active subscription plan', 'status': HTTP_400_BAD_REQUEST})


class UpdateSubscriptionStatus(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = SubscriptionStatus

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        try:
            subscription_obj = SubscriptionStatus.objects.get(user=r_user)
            subscription_obj.active = self.request.POST['active'].title()
            subscription_obj.purchase_token = self.request.POST['purchase_token']
            subscription_obj.save()
            try:
                transaction_obj = Transaction.objects.get(purchase_token=self.request.POST['purchase_token'])
                if transaction_obj.purchase_token == self.request.POST['purchase_token']:
                    return Response({'message': 'Subscription status updated successfully', 'purchased_status': True,
                                     'status': HTTP_200_OK})
                else:
                    return Response({'message': 'Subscription status updated successfully', 'purchased_status': False,
                                     'status': HTTP_400_BAD_REQUEST})
            except Exception as e:
                return Response({'message': 'Subscription status updated successfully', 'purchased_status': False,
                                 'status': HTTP_400_BAD_REQUEST})
        except Exception as e:
            print(e)
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})

# class VerifyApplePurchase(APIView):
#     def get(self, request, *args, **kwargs):
#         requestBody = {}
#         receipt_id = self.request.GET.get('receipt_id')
#         requestBody["receipt-data"] = receipt_id
#         url = 'https://sandbox.itunes.apple.com/verifyReceipt'
#         shared_secret = '099eddbf89bf4c53b2ec8d9bce1df11d'
#         requestBody["password"] = shared_secret
#
#         http = urllib3.PoolManager()
#         response = http.request("POST", url, headers={"content-type": "application/json"},
#                                 body=json.dumps(requestBody).encode("utf-8"))
#         print(json.loads(response.data))
#         if response.status == 200:
#             responseBody = json.loads(response.data)
#             status = responseBody.get("status")
#             print(status)
#             return Response({'message': responseBody})
#         else:
#             print(f" Error: {response.status}")
#             return Response({'Error': response.status, 'status': HTTP_400_BAD_REQUEST})
#     # def get(self, request, *args, **kwargs):
#     #     from inapppy import AppStoreValidator, InAppPyValidationError
#     #     receipt_id = self.request.GET.get('receipt_id')
#     #     bundle_id = 'com.maclo.app'
#     #     auto_retry_wrong_env_request = False  # if True, automatically query sandbox endpoint if
#     #     # validation fails on production endpoint
#     #     validator = AppStoreValidator(bundle_id, auto_retry_wrong_env_request=auto_retry_wrong_env_request)
#     #
#     #     try:
#     #         exclude_old_transactions = False  # if True, include only the latest renewal transaction
#     #         validation_result = validator.validate(receipt_id, '099eddbf89bf4c53b2ec8d9bce1df11d',
#     #                                                exclude_old_transactions=exclude_old_transactions)
#     #     except InAppPyValidationError as ex:
#     #         # handle validation error
#     #         response_from_apple = ex.raw_response  # contains actual response from AppStore service.
#     #         # pass
#     #         return Response({'data':response_from_apple})
#
#
# def process_purchases(purchases):
#     process(*purchases) if isinstance(purchases, list) else process(purchases)
#
#
# def process(*purchases):
#     for p in purchases:
#         print(p)
#
#
# class VerfiyGooglePurchase(APIView):
#
#     # def get(self, request, *args, **kwargs):
#     #     from google.oauth2.credentials import Credentials
#     #     from googleapiclient.discovery import build
#     #     credentials = Credentials.from_service_account_file(
#     #         "service_account.json")
#     #     service = googleapiclient.discovery.build("androidpublisher", "v3", credentials=credentials)
#     #
#     #     # Use the token your API got from the app to verify the purchase
#     #     result = service.purchases().subscriptions().get(packageName="com.dating.maclo", subscriptionId="maclo_star_1month",
#     #                                                      token="ifefnfdopngciodhgkfkojfa.AO-J1OwnDmM0FqeiCjs7eF3G7bK6pG2--WzzUIB2JQyGTMFskw9x1dsW00FXIzYma1epgca_WDdmq2bU5nr9gxE8kTWHHJXfeg").execute()
#     #     return Response({'message': result, 'status': HTTP_200_OK})
#     def get(self, request, *args, **kwargs):
#         from inapppy import GooglePlayValidator, InAppPyValidationError
#
#         # bundle_id = 'com.dating.maclo'
#         bundle_id = 'com.dating.maclo'
#         api_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAp14BNCg9jbkAXFV102f4dMUm+/e7vCu05cpedD3Oq5PvPhT5fn4jo6XuA3mVhYQymWIEVK+7zh7Ok994jFBOWVAWyGoD3WjDCd+knb9A3QqP3tFD+Ph8cxqifzyx6UWsH/+PDV8OZNIxJGpKrEaXYmLZB4tNMJjFSxC6zMtEsKsTTXTT2Tngh066CwUX1e4pFNuHud90dFs8sysY+7oYLZz1F079pWiQLTX973a74AiGlkwOMOWHOe0G6dOslbXfhRBMHjP4SNurs+6+vhdVkFREiPcFhRELVmUcKUw5zSiqNKi4h+vun8lcxQ6MmLjb45enS6iE73KbHSmZe6JDCwIDAQAB'
#         # validator = GooglePlayValidator(bundle_id, api_key)
#         # d = '{ "type": "service_account","project_id":"pc-api-4867801607121608246-604","private_key_id":"bf4e9a7684bc510ffb643b61f367d97bc41ecc3e","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDI1jt90AVCmhyj\nJ4olx+B8pO9cgLlIovFZw5UQF2ZYXmUSp66p9yj53UnomXufNNGizZPKF7xzKO7p\n4BcsR1L/rK+hUtrIQzqWVzSxNzLVdMS0Xv1jSjJLRYlX9R7M99Hrk/rgIOpgy8mi\nmNatTA/AmsKOjgFSE++u9j/d5tUgAn8ROQ6aErgxIVggfOFFImHsLWDYb+JX9Coa\nkHSlWCIc64A1b5fQHvP8Y/dbNvHBnAkZ183bK90gLqT2gZtqnT36X2gsTTFHe/1u\nLeaPTqphQxl3f5KR9HKsyQhWQDy0tF+qELHSQUvTXj0YwQGqnXMz9+80O7iSHSNe\n2RWbDfobAgMBAAECggEANa41Vop8bXHdx6ow3apQEWDQbawmWgjbc7+4HwXyIBqS\n72qMX/elJywDrj0f8szeX6KNJw4zG6DMQwzXhMlHoPkaNId93NtDVJ3YgqmbV7yP\nOxrMpXZWfRIIBM+KvQRcQphaDQAfRWIS8ffiIY3cBAIZkJraNYMIpH5DUd96BcTL\nsuql/g/nw4/G16laYz5rd40r6IEa7F7+vScmpr1tGiiOzad9bQWD99yZzsXh2W38\nkLa5/Ncb7ijWEIqDN1J6b3Q4WKhlzzy1G0UopsCgfybytspfNa4CPW2XrESSVffX\no+pM0V+eB//cM4+Hu6KOme5oeylJuuFxJ3E13ZcngQKBgQDtqGcOsFfKMD4Xzs6G\nzZqeUeSwyvhXzlKNDR62ggu4NkQ1gUjz4iqRPboAffFrgzDg6djREfWLRsJjgJTL\nK2vaQr+7pQWhwtk4xSsGTbNpUM1ZzIcmGWB1l1ozVq0jzYiHOhQ6614pQ2oBCFTI\nZwc3qZ87vADbFBjKA3TzjQWm2wKBgQDYVlP7MmE2795g9g+Jy02AM5vOu6BS2ZK4\nRuUgRmatklVg+RFrSpTWS42D1EJQk0WkV0oyh4TnkdSZXE/uhAB6j39oh4+aR5WC\nCJmYXpUrwoAY/qarwCB6TtN3EuQnhixN4dGER2EtllAY/4SRI0jrSSbQ8ELcYQx9\nHrx1Mus9wQKBgQDqt4WBFly+DcNllBSZQnrQniT1DqETZ2xUbn7E1c9pUf8vsM4y\nQE62P3ZygfBrtJgTqiE+6zPNKEdYKmfJ+Mp+N6pRUvwq9NvAm8qQYTEudGU7qSpZ\nUHrZ6G9ngNVjJN0QYSYVwtuueSw6dNX3Tvnr2ZSwVE+sDz8kVSGuYLsSPQKBgEn2\nScQJ116252py9aEAlsCL5GrrjsaEiDrkUhWUvCn/a505yhDKcNRLBFjbyshNcXPc\nPAvGdVPOccb03ocHLjq4sLCGGDyA2MaaNhj3zTwmxTDGbyktCG2IYZfGJ6azopYF\n7GGzHbA+QagqQ6JzU8zNN64bVmCN9X0ZcwkGnZKBAoGAIMRohAWOJTt2tGOgIr6m\nz8/pqT8STBqKZZ9SwTilPMSzfaISdiayBC3M9h7V6XYeZQ6VBpnDmeohZJP0pfd8\nIDkYYAV9iIADDjXljolbrVKkozvabpi/MA/q6QAxBzRyKpwXYJBiEniGw1pz22+i\nqS+MnxKej5nUaButhe6XVQM=\n-----END PRIVATE KEY-----\n","client_email":"mymacloserviceaccount@pc-api-4867801607121608246-604.iam.gserviceaccount.com","client_id":"100730210319475150612","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/mymacloserviceaccount%40pc-api-4867801607121608246-604.iam.gserviceaccount.com"}'
#         # d = '{''"type": "service_account",'\
#         #         '"project_id": "pc-api-4867801607121608246-604",'\
#         #         '"private_key_id": "bf4e9a7684bc510ffb643b61f367d97bc41ecc3e",'\
#         #         '"private_key": "-----BEGIN PRIVATE KEY-----\nnMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDI1jt90AVCmhyj\nJ4olx+B8pO9cgLlIovFZw5UQF2ZYXmUSp66p9yj53UnomXufNNGizZPKF7xzKO7p\n4BcsR1L/rK+hUtrIQzqWVzSxNzLVdMS0Xv1jSjJLRYlX9R7M99Hrk/rgIOpgy8mi\nmNatTA/AmsKOjgFSE++u9j/d5tUgAn8ROQ6aErgxIVggfOFFImHsLWDYb+JX9Coa\nkHSlWCIc64A1b5fQHvP8Y/dbNvHBnAkZ183bK90gLqT2gZtqnT36X2gsTTFHe/1u\nLeaPTqphQxl3f5KR9HKsyQhWQDy0tF+qELHSQUvTXj0YwQGqnXMz9+80O7iSHSNe\n2RWbDfobAgMBAAECggEANa41Vop8bXHdx6ow3apQEWDQbawmWgjbc7+4HwXyIBqS\n72qMX/elJywDrj0f8szeX6KNJw4zG6DMQwzXhMlHoPkaNId93NtDVJ3YgqmbV7yP\nOxrMpXZWfRIIBM+KvQRcQphaDQAfRWIS8ffiIY3cBAIZkJraNYMIpH5DUd96BcTL\nsuql/g/nw4/G16laYz5rd40r6IEa7F7+vScmpr1tGiiOzad9bQWD99yZzsXh2W38\nkLa5/Ncb7ijWEIqDN1J6b3Q4WKhlzzy1G0UopsCgfybytspfNa4CPW2XrESSVffX\no+pM0V+eB//cM4+Hu6KOme5oeylJuuFxJ3E13ZcngQKBgQDtqGcOsFfKMD4Xzs6G\nzZqeUeSwyvhXzlKNDR62ggu4NkQ1gUjz4iqRPboAffFrgzDg6djREfWLRsJjgJTL\nK2vaQr+7pQWhwtk4xSsGTbNpUM1ZzIcmGWB1l1ozVq0jzYiHOhQ6614pQ2oBCFTI\nZwc3qZ87vADbFBjKA3TzjQWm2wKBgQDYVlP7MmE2795g9g+Jy02AM5vOu6BS2ZK4\nRuUgRmatklVg+RFrSpTWS42D1EJQk0WkV0oyh4TnkdSZXE/uhAB6j39oh4+aR5WC\nCJmYXpUrwoAY/qarwCB6TtN3EuQnhixN4dGER2EtllAY/4SRI0jrSSbQ8ELcYQx9\nHrx1Mus9wQKBgQDqt4WBFly+DcNllBSZQnrQniT1DqETZ2xUbn7E1c9pUf8vsM4y\nQE62P3ZygfBrtJgTqiE+6zPNKEdYKmfJ+Mp+N6pRUvwq9NvAm8qQYTEudGU7qSpZ\nUHrZ6G9ngNVjJN0QYSYVwtuueSw6dNX3Tvnr2ZSwVE+sDz8kVSGuYLsSPQKBgEn2\nScQJ116252py9aEAlsCL5GrrjsaEiDrkUhWUvCn/a505yhDKcNRLBFjbyshNcXPc\nPAvGdVPOccb03ocHLjq4sLCGGDyA2MaaNhj3zTwmxTDGbyktCG2IYZfGJ6azopYF\n7GGzHbA+QagqQ6JzU8zNN64bVmCN9X0ZcwkGnZKBAoGAIMRohAWOJTt2tGOgIr6m\nz8/pqT8STBqKZZ9SwTilPMSzfaISdiayBC3M9h7V6XYeZQ6VBpnDmeohZJP0pfd8\nIDkYYAV9iIADDjXljolbrVKkozvabpi/MA/q6QAxBzRyKpwXYJBiEniGw1pz22+i\nqS+MnxKej5nUaButhe6XVQM==\n-----END PRIVATE KEY-----\n",''   "client_email": "mymacloserviceaccount@pc-api-4867801607121608246-604.iam.gserviceaccount.com",''   "client_id": "100730210319475150612",''   "auth_uri": "https://accounts.google.com/o/oauth2/auth",''   "token_uri": "https://oauth2.googleapis.com/token",'\
#         #         '"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",'\
#         #         '"client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mymacloserviceaccount%40pc-api-4867801607121608246-604.iam.gserviceaccount.com"'\
#         #         '}'
#         # api_credentials = json.loads(d)
#         # validator = GooglePlayValidator(bundle_id, api_credentials)
#         validator = GooglePlayValidator(bundle_id, api_key)
#
#         # try:
#         #     # receipt means `androidData` in result of purchase
#         #     # signature means `signatureAndroid` in result of purchase
#         #     receipt = {"orderId": "GPA.3372-9954-3755-32447", "packageName": "com.dating.maclo",
#         #                "productId": "maclo_star_1month", "purchaseTime": 1623130886567, "purchaseState": 0,
#         #                "purchaseToken": "dhjialflfogjpogmnjjfadke.AO-J1OwBi1-UZOzXYAfAhBsrtsPxC4Qz8QEwj6sVIlF1fdHRzZedB64sJuqkUYvj74NmH3A5UkZw5mfOBBMDbtyo5Y85GoaWzQ",
#         #                "autoRenewing": True, "acknowledged": False}
#         #     signature = {
#         #         'signature': 'RGFV/yJuAB5FXhsuBRMULtUhR4kCCG8+HixM1XTY4BN2lDDmRI5TNAY4PPFbLBpUjWrRbY3Atsovnw3N+EsdCtRsZPaTbiEQtsT5ky1OB3IxUgbo93KkLEym1zfwS+k8IBg+HCAYpiL0wSaqH8Z9Y58XPYyvP3nurL5EWTKf8aqT8NCpgqaBIopQ3i8W6CGwHVAF54+dyeFbQH2tKbBun0jjnXCa1tTs/wUeS3vYyOXDvKqmBm8/ji75fIL/5prxeGeccusV4sH6aiJ0MD6cFD9495IQ2euN+qaqfxYnhHIpgPnC054HVUNyI4qQBJ9qAK4Pv6GUOZTE+WByA76D7w=='}
#         #     validation_result = validator.validate('dhjialflfogjpogmnjjfadke.AO-J1OwBi1-UZOzXYAfAhBsrtsPxC4Qz8QEwj6sVIlF1fdHRzZedB64sJuqkUYvj74NmH3A5UkZw5mfOBBMDbtyo5Y85GoaWzQ', 'RGFV/yJuAB5FXhsuBRMULtUhR4kCCG8+HixM1XTY4BN2lDDmRI5TNAY4PPFbLBpUjWrRbY3Atsovnw3N+EsdCtRsZPaTbiEQtsT5ky1OB3IxUgbo93KkLEym1zfwS+k8IBg+HCAYpiL0wSaqH8Z9Y58XPYyvP3nurL5EWTKf8aqT8NCpgqaBIopQ3i8W6CGwHVAF54+dyeFbQH2tKbBun0jjnXCa1tTs/wUeS3vYyOXDvKqmBm8/ji75fIL/5prxeGeccusV4sH6aiJ0MD6cFD9495IQ2euN+qaqfxYnhHIpgPnC054HVUNyI4qQBJ9qAK4Pv6GUOZTE+WByA76D7w==')
#         #     print(validation_result)
#         # except InAppPyValidationError as e:
#         # handle validation error
#         # pass
#         # print(e)
#         from pyinapp import GooglePlayValidator, InAppValidationError
#
#         bundle_id = 'com.dating.maclo'
#         api_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAp14BNCg9jbkAXFV102f4dMUm+/e7vCu05cpedD3Oq5PvPhT5fn4jo6XuA3mVhYQymWIEVK+7zh7Ok994jFBOWVAWyGoD3WjDCd+knb9A3QqP3tFD+Ph8cxqifzyx6UWsH/+PDV8OZNIxJGpKrEaXYmLZB4tNMJjFSxC6zMtEsKsTTXTT2Tngh066CwUX1e4pFNuHud90dFs8sysY+7oYLZz1F079pWiQLTX973a74AiGlkwOMOWHOe0G6dOslbXfhRBMHjP4SNurs+6+vhdVkFREiPcFhRELVmUcKUw5zSiqNKi4h+vun8lcxQ6MmLjb45enS6iE73KbHSmZe6JDCwIDAQAB'
#         validator = GooglePlayValidator(bundle_id, api_key)
#         receipt = {"orderId": "GPA.3372-9954-3755-32447", "packageName": "com.dating.maclo",
#                    "productId": "maclo_star_1month", "purchaseTime": 1623130886567, "purchaseState": 0,
#                    "purchaseToken": "dhjialflfogjpogmnjjfadke.AO-J1OwBi1-UZOzXYAfAhBsrtsPxC4Qz8QEwj6sVIlF1fdHRzZedB64sJuqkUYvj74NmH3A5UkZw5mfOBBMDbtyo5Y85GoaWzQ",
#                    "autoRenewing": True, "acknowledged": False}
#         try:
#             purchases = validator.validate(
#                 'dhjialflfogjpogmnjjfadke.AO-J1OwBi1-UZOzXYAfAhBsrtsPxC4Qz8QEwj6sVIlF1fdHRzZedB64sJuqkUYvj74NmH3A5UkZw5mfOBBMDbtyo5Y85GoaWzQ',
#                 'RGFV/yJuAB5FXhsuBRMULtUhR4kCCG8+HixM1XTY4BN2lDDmRI5TNAY4PPFbLBpUjWrRbY3Atsovnw3N+EsdCtRsZPaTbiEQtsT5ky1OB3IxUgbo93KkLEym1zfwS+k8IBg+HCAYpiL0wSaqH8Z9Y58XPYyvP3nurL5EWTKf8aqT8NCpgqaBIopQ3i8W6CGwHVAF54+dyeFbQH2tKbBun0jjnXCa1tTs/wUeS3vYyOXDvKqmBm8/ji75fIL/5prxeGeccusV4sH6aiJ0MD6cFD9495IQ2euN+qaqfxYnhHIpgPnC054HVUNyI4qQBJ9qAK4Pv6GUOZTE+WByA76D7w==')
#             process_purchases(purchases)
#         except InAppValidationError as e:
#             """ handle validation error """
#             return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
#
#
# class GoogleVerification(APIView):
#     def get(self, request, *args, **kwargs):
#         from googleapiclient.discovery import build
#         from googleapiclient.errors import HttpError
#         from oauth2client.service_account import ServiceAccountCredentials
#         DEFAULT_AUTH_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
#         credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json")
#         service = googleapiclient.discovery.build("androidpublisher", "v3", credentials=credentials)
#
#         # Use the token your API got from the app to verify the purchase
#         result = service.purchases().subscriptions().get(packageName="pc-api-4867801607121608246-604",
#                                                          subscriptionId="sku.name",
#                                                          token="ipdpjbllgieimolmjhogncdh.AO-J1OyJGhyOIy_IWPBP4ri3vQ5XklebY5sgutSHXlnlylQzHCYb4nbA-VDe4hNkb_dV-BVrfy0DEkHJPGM37s8pOf7bsz51-A").execute()
#         print(result)
#         return Response(str(result))
#
#
# class TestVerifyInappPurchase(APIView):
#     def get(self, request, *args, **kwargs):
#         from oauth2client.service_account import ServiceAccountCredentials
#         from httplib2 import Http
#         from googleapiclient.discovery import build
#
#         scopes = ['https://www.googleapis.com/auth/androidpublisher']
#         # with open('/home/mobulous/Desktop/Maclo-Dating-App/src/service_account.json', 'r') as f:
#         credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/mobulous/Desktop/Maclo-Dating-App/src/maclodatingapp.json', scopes)
#
#         http_auth = credentials.authorize(Http())
#
#         androidpublisher = build('androidpublisher', 'v3', http=http_auth)
#         product = androidpublisher.purchases().products().get(productId="maclo_star_1month",
#                                                               packageName="com.dating.maclo",
#                                                               token="gpklhdcaicndfeifpnocnijd.AO-J1OxAGbm4K8uFeLTQL3Ya1a5XyfjMX3rrgH3wOxX7E8eJJmRGZNp8L1HV8dA6GoEXsas7UYtp918hjwIlvIzvy5PbEsVKLg")
#
#         purchase = product.execute()
#         print(purchase.data)
#         # https: // androidpublisher.googleapis.com / androidpublisher / v3 / applications / {
#         #     packageName} / purchases / subscriptions / {subscriptionId} / tokens / {token}
#         return Response(str(purchase))
