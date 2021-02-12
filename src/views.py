import os
import shutil

import instaloader
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from .fcm_notification import send_to_one, send_another
from adminpanel.models import UserNotification
from .models import UserInstagramPic, UserDetail, RegisterUser, MatchedUser, RequestMeeting, ScheduleMeeting, Feedback, \
    AboutUs, ContactUs, SubscriptionPlans, ContactUsQuery, DeactivateAccount, BlockedUsers
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
            user = User.objects.get(phone_number=phone_number)
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
        # user = self.request.user
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
        register_id.date_of_birth = request.data.get("date_of_birth")
        register_id.qualification = request.data.get("qualification")
        register_id.religion = request.data.get("religion")
        register_id.body_type = request.data.get("body_type")
        register_id.relationship_status = request.data.get("relationship_status")
        register_id.fav_quote = request.data.get("fav_quote")
        register_id.save(
            update_fields=['date_of_birth', 'qualification', 'religion', 'body_type', 'relationship_status',
                           'fav_quote'])
        print(register_id.pic_1)
        print(register_id.pic_2)
        print(register_id.pic_3)
        print(register_id.pic_4)
        print(register_id.pic_5)
        print(register_id.pic_6)
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
        return Response({"Success": "Images uploaded from instagram successfully", "status": HTTP_200_OK})


class ShowInstagramPics(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShowInstaPics

    def get(self, request, *args, **kwargs):
        # id = self.request.GET.get('phone_number')
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
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
        qualification = self.request.GET.get('qualification' or None)
        relationship_status = self.request.GET.get('relationship_status' or None)
        religion = self.request.POST.get('religion' or None)
        body_type = self.request.POST.get('body_type' or None)
        gender = self.request.POST.get('gender' or None)
        height = self.request.POST.get('height' or None)
        zodiac_sign = self.request.POST.get('zodiac_sign' or None)
        taste = self.request.POST.get('taste' or None)
        print('qualification--->>>', qualification)
        print('relationship_status---->>', relationship_status)
        print('religion---->>', religion)
        print('body_type--->>', body_type)
        print('gender--->>>', gender)
        print('height--->>>', height)
        print('zodiac_sign--->>', zodiac_sign)
        print('taste____>>>', taste)
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
        if qualification or relationship_status or height or gender or religion or zodiac_sign or taste or body_type:
            for y in z:
                if y.qualification == qualification or y.relationship_status == relationship_status or y.height == height or y.gender == gender or y.religion == religion or y.zodiac_sign == zodiac_sign or y.body_type == body_type or y.taste == taste:
                    qs.append(y)
                else:
                    pass
        else:
            qs = z
        final_list = []
        print('QS_____________>>>>>>>>>>', qs)
        for y in qs:
            a = UserDetail.objects.get(phone_number=y.id)
            final_list.append(a)
        print('FINAL LIST ----->>>', final_list)
        filtered_users = []
        for obj in final_list:
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
        queryset = UserDetail.objects.filter(id=phone_number)
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
            # interests = obj.phone_number.interests
            fav_quote = obj.phone_number.fav_quote
            religion = obj.phone_number.religion
            body_type = obj.phone_number.body_type
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
                # "interests": interests,
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
                # "subscription": subscription
            }
            return Response({"Details": detail}, status=HTTP_200_OK)
        return Response({"Details": queryset}, status=HTTP_200_OK)


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
                body="You have been liked by " + from_user_name
            )
            fcm_token = User.objects.get(email=to_user_id.email).device_token
            try:
                title = "Like Notification"
                body = "You have been liked by " + from_user_name
                message_type = "likeNotification"
                respo = send_another(fcm_token, title, body, message_type)
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
                    body="You have been matched by " + from_user_name
                )
                fcm_token = User.objects.get(email=to_user_id.email).device_token
                try:
                    title = "Match Notification"
                    body = "You have been matched with " + from_user_name
                    message_type = "matchNotification"
                    respo = send_another(fcm_token, title, body, message_type)
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
                body="You have been super liked by " + from_user_name
            )
            fcm_token = User.objects.get(email=to_user_id.email).device_token
            try:
                title = "Super Like Notification"
                body = "You have been super liked by " + from_user_name
                message_type = "superLike"
                respo = send_another(fcm_token, title, body, message_type)
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
                    body="You have been super matched by " + from_user_name
                )
                fcm_token = User.objects.get(email=to_user_id.email).device_token
                try:
                    title = "Super Like Notification"
                    body = "You have been super matched with " + from_user_name
                    message_type = "superMatch"
                    respo = send_another(fcm_token, title, body, message_type)
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
                print('EXCEPT BLOCK Match--------------', len(match_with | match_by))
                print('ID BLOCK Match--------------', [x.id for x in y.liked_by_me.all()])
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
        return Response({'match': z + a, 'status': HTTP_200_OK})


class UserLikedList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        like_list = []
        super_like_list = []
        liked_users = MatchedUser.objects.filter(user=r_user)
        for user in liked_users:
            if len(user.liked_by_me.all()) > 0:
                print(user.liked_by_me.all()[0].id)
                print(user.liked_by_me.all().first().id)
                z = RegisterUser.objects.get(id=user.liked_by_me.all().first().id)
                if z.id not in like_list:
                    print(z.id)
                    if z.pic_1:
                        like_list.append(
                            {'id': z.id, 'first_name': z.first_name, 'last_name': z.last_name,
                             'liked_at': user.matched_at,
                             'profile_pic': z.pic_1.url, 'type': 'like'})
                    else:
                        like_list.append(
                            {'id': z.id, 'first_name': z.first_name, 'last_name': z.last_name,
                             'liked_at': user.matched_at,
                             'profile_pic': '', 'type': 'like'})
                else:
                    pass

            if len(user.super_liked_by_me.all()) > 0:
                print(user.super_liked_by_me.all()[0].id)
                print(user.super_liked_by_me.all().first().id)
                z = RegisterUser.objects.get(id=user.super_liked_by_me.all().first().id)
                if z.id not in super_like_list:
                    print(z.id)
                    if z.pic_1:
                        super_like_list.append(
                            {'id': z.id, 'first_name': z.first_name, 'last_name': z.last_name,
                             'liked_at': user.matched_at,
                             'profile_pic': z.pic_1.url, 'type': 'super_like'})
                    else:
                        super_like_list.append(
                            {'id': z.id, 'first_name': z.first_name, 'last_name': z.last_name,
                             'liked_at': user.matched_at,
                             'profile_pic': '', 'type': 'super_like'})
                else:
                    pass
        return Response({'data': like_list + super_like_list, 'status': HTTP_200_OK})


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
                notification_body="You have a meeting request from " + first_name

            )
            return Response({"Request sent successfully"}, status=HTTP_200_OK)
        else:
            return Response({"Cannot send request as the user is not a match"}, status=HTTP_400_BAD_REQUEST)


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
                              from_user_name + ' has changed to  ' + status
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
            body="You have a meeting request from " + from_user_name
        )
        fcm_token = User.objects.get(email=requested_user.email).device_token
        try:
            title = "Meeting Request"
            body = "You have a meeting request from " + from_user_name
            message_type = "superLike"
            respo = send_another(fcm_token, title, body, message_type)
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
        meeting_id = self.request.data['meeting_id']
        meeting_obj = ScheduleMeeting.objects.get(id=meeting_id)
        if meeting_obj.scheduled_by.pic_1 and meeting_obj.scheduled_with.pic_1:
            return Response(
                {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': meeting_obj.scheduled_by.pic_1.url,
                 'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                 'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                 'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                 'invitee_first_name': meeting_obj.scheduled_with.first_name,
                 'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                 'date': meeting_obj.meeting_date, 'description': meeting_obj.description, 'venue': meeting_obj.venue,
                 'status': HTTP_200_OK})
        elif meeting_obj.scheduled_by.pic_1:
            return Response(
                {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': '',
                 'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                 'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                 'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': meeting_obj.scheduled_with.pic_1.url,
                 'invitee_first_name': meeting_obj.scheduled_with.first_name,
                 'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                 'date': meeting_obj.meeting_date, 'description': meeting_obj.description, 'venue': meeting_obj.venue,
                 'status': HTTP_200_OK})
        else:
            return Response(
                {'invited_by': meeting_obj.scheduled_by.id, 'invited_by_pic': meeting_obj.scheduled_by.pic_1.url,
                 'invited_by_first_name': meeting_obj.scheduled_by.first_name,
                 'invited_by_last_name': meeting_obj.scheduled_by.last_name,
                 'invitee_id': meeting_obj.scheduled_with.id, 'invitee_pic': '',
                 'invitee_first_name': meeting_obj.scheduled_with.first_name,
                 'invitee_last_name': meeting_obj.scheduled_with.last_name, 'time': meeting_obj.meeting_time,
                 'date': meeting_obj.meeting_date, 'description': meeting_obj.description, 'venue': meeting_obj.venue,
                 'status': HTTP_200_OK})


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
            if RegisterUser.objects.get(id=meeting.scheduled_by.id).pic_1:
                if RegisterUser.objects.get(id=meeting.scheduled_by.id).id in final_blocked_users_list:
                    recevied_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                         'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_by.id).pic_1.url,
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'received', 'blocked': True})
                else:
                    recevied_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                         'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_by.id).pic_1.url,
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'received', 'blocked': False})
            else:
                if RegisterUser.objects.get(id=meeting.scheduled_by.id).id in final_blocked_users_list:
                    recevied_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                         'profile_pic': '',
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'received', 'blocked': True})
                else:
                    recevied_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_by.id).last_name,
                         'profile_pic': '',
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'received', 'blocked': False})
        for meeting in meeting_request_sent:
            if RegisterUser.objects.get(id=meeting.scheduled_with.id).pic_1:
                if RegisterUser.objects.get(id=meeting.scheduled_with.id).id in final_blocked_users_list:
                    sent_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                         'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_with.id).pic_1.url,
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'sent', 'blocked': True})
                else:
                    sent_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                         'profile_pic': RegisterUser.objects.get(id=meeting.scheduled_with.id).pic_1.url,
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'sent', 'blocked': False})
            else:
                if RegisterUser.objects.get(id=meeting.scheduled_with.id).id in final_blocked_users_list:
                    sent_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                         'profile_pic': '',
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'sent', 'blocked': True})
                else:
                    sent_list.append(
                        {'id': meeting.id,
                         'first_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).first_name,
                         'last_name': RegisterUser.objects.get(id=meeting.scheduled_with.id).last_name,
                         'profile_pic': '',
                         'date': meeting.meeting_date, 'time': meeting.meeting_time, 'status': meeting.status,
                         'type': 'sent', 'blocked': False})
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
            body="Your meeting request has been {} by {}".format(status, meeting.scheduled_with.first_name)
        )
        fcm_token = User.objects.get(email=meeting.scheduled_by.email).device_token
        try:
            title = "Meeting Status"
            body = "Your meeting request has been {} by {}".format(status, meeting.scheduled_with.first_name)
            message_type = "superLike"
            respo = send_another(fcm_token, title, body, message_type)
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
        r_user = RegisterUser.objects.get(email=self.request.user.email)
        user_detail = UserDetail.objects.get(phone_number=r_user)
        user_detail.discovery = fromstr(f'POINT({lang} {lat})', srid=4326)
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


class ContactUsApiView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ContactUs
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()


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
        # profile_pic = self.request.POST.get('profile_pic' or None)
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
                    "interested": user_detail.interest
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
                reg_usr = RegisterUser.objects.create(
                    email=email,
                    first_name=name,
                    date_of_birth=dob
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
                    "interested": user_detail.interest
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
                reg_usr = RegisterUser.objects.create(
                    email=email,
                    first_name=name,
                    date_of_birth=dob
                )
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
                meeting = ScheduleMeeting.objects.get(scheduled_with=user1, scheduled_by=user2)
                return Response({'meeting_exists': True, 'meeting_id': meeting.id, 'status': HTTP_200_OK})
            except Exception as e:
                meeting = ScheduleMeeting.objects.get(scheduled_with=user2, scheduled_by=user1)
                return Response({'meeting_exists': True, 'meeting_id': meeting.id, 'status': HTTP_200_OK})
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
