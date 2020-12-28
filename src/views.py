import os
import shutil

import instaloader
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import UserInstagramPic, UserDetail, RegisterUser, MatchedUser, RequestMeeting, ScheduleMeeting, Feedback, \
    AboutUs, ContactUs, InAppNotification, SubscriptionPlans
from .serializers import (UserDetailSerializer, UserInstagramSerializer, RegisterSerializer,
                          MatchedUserSerializer, LikeSerializer, DeleteMatchSerializer, SuperLikeSerializer,
                          RequestMeetingSerializer, ScheduleMeetingSerializer, FeedbackSerializer, ContactUsSerializer,
                          AboutUsSerializer, MeetingStatusSerializer, PopUpNotificationSerializer,
                          SubscriptionPlanSerializer, DeleteSuperMatchSerializer, SearchSerializer,
                          GetInstagramPicSerializer, SocialUserSerializer, ShowInstaPics, AuthTokenSerializer,
                          FacebookSerializer, GmailSerializer)

User = get_user_model()


class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        phone_number = self.request.data['phone_number']
        x = {}
        try:
            user = User.objects.get(phone_number=phone_number)
            if user:
                token = Token.objects.get_or_create(user=user)
                print(token)
                print(token[0].key)
                return Response({'token': token[0].key, 'status': HTTP_200_OK})
        except Exception as e:
            x = {"Error": str(e)}
            return Response({'message': x['Error'], "status": HTTP_400_BAD_REQUEST})
        return Response({'message': x['Error'], "status": HTTP_400_BAD_REQUEST})


@method_decorator(csrf_exempt, name='dispatch')
class UserCreateAPIView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=self.request.data)
        first_name = self.request.data['first_name']
        last_name = self.request.data['last_name']
        phone_number = self.request.data['phone_number']
        gender = self.request.data['gender']
        date_of_birth = self.request.data['date_of_birth']
        # job_profile = self.request.data['job_profile']
        # company_name = self.request.data['company_name']
        email = self.request.data['email']
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
            UserDetail.objects.create(
                phone_number=user
            )
            us_obj = User.objects.create(
                email=email,
                phone_number=phone_number
            )
            us_obj.set_password(phone_number)
            us_obj.save()
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
            if user_data.pic_7:
                pic_7 = user_data.pic_8.url
            else:
                pic_7 = ''
            if user_data.pic_8:
                pic_8 = user_data.pic_8.url
            else:
                pic_8 = ''
            if user_data.pic_9:
                pic_9 = user_data.pic_9.url
            else:
                pic_9 = ''
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
                "pic_7": pic_7,
                "pic_8": pic_8,
                "pic_9": pic_9,
            }
            return Response({"User": "User Created successfully", "Data": Data, "status": HTTP_201_CREATED})


# class GetUserToken(ObtainAuthToken):
#     serializer_class = GetUserTokenSerializer

#     def post(self, request, *args, **kwargs):
#         phone_number = self.request.data['phone_number']
#         user = RegisterUser.objects.get(phone_number=phone_number).user
#         print('--------------->>>>>>',user)
#         try:
#             user_with_token = Token.objects.get(user=user)
#             print('TRY-------------->>>',user_with_token)
#             if user_with_token:
#                 print('TRY If-------------->>>',user_with_token)
#                 return Response({"Token": user_with_token.key})
#         except Exception as e:
#             print(e)
#             token = Token.objects.create(user=user)
#             print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', token)
#             return Response({"Token": token.key}, status=HTTP_200_OK)

class UpdatePhoneNumber(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.phone_number = request.data.get('phone_number')
        instance.save(update_fields=['phone_number'])
        logged_in_user_id = self.request.data['id']
        from_id = logged_in_user_id
        from_user_id = RegisterUser.objects.get(id=from_id)
        from_user_name = from_user_id.first_name
        phone_number = self.request.data['phone_number']
        to_user = RegisterUser.objects.get(id=phone_number)
        first_name = to_user.first_name
        to_id = self.request.data['phone_number']
        to_user_id = RegisterUser.objects.get(id=to_id)
        InAppNotification.objects.create(
            from_user_id=from_user_id,
            from_user_name=from_user_name,
            to_user_id=to_user_id,
            to_user_name=first_name,
            notification_type="Phone Number Update",
            notification_title="Phone Number",
            notification_body="Your Phone number has been updated"
        )
        return Response({"Your phone number has been update"}, status=HTTP_200_OK)


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
                "id": user.id,
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
                "interests": user.phone_number.interests,
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
        instance = self.get_object()
        instance.bio = request.data.get("bio")
        instance.living_in = request.data.get("living_in")
        instance.hometown = request.data.get("hometown")
        instance.profession = request.data.get("profession")
        instance.college_name = request.data.get("college_name")
        instance.university = request.data.get("university")
        instance.personality = request.data.get("personality")
        instance.preference_first_date = request.data.get(
            "preference_first_date")
        instance.fav_music = request.data.get("fav_music")
        instance.food_type = request.data.get("food_type")
        instance.owns = request.data.get("owns")
        instance.travelled_place = request.data.get("travelled_place")
        instance.once_in_life = request.data.get("once_in_life")
        instance.exercise = request.data.get("exercise")
        instance.looking_for = request.data.get("looking_for")
        instance.fav_food = request.data.get("fav_food")
        instance.fav_pet = request.data.get("fav_pet")
        instance.smoke = request.data.get("smoke")
        instance.drink = request.data.get("drink")
        instance.subscription_purchased = request.data.get(
            "subscription_purchased")
        instance.subscription_purchased_at = request.data.get(
            "subscription_purchased_at")
        id = request.data.get("subscription")
        id = int(id)
        subscription = SubscriptionPlans.objects.get(id=id)
        instance.subscription = subscription
        instance.save(
            update_fields=['bio', 'phone_number', 'living_in', 'hometown', 'profession', 'college_name',
                           'university',
                           'personality', 'preference_first_date', 'fav_music', 'travelled_place',
                           'once_in_life', 'exercise', 'looking_for', 'fav_food', 'owns', 'food_type', 'fav_pet',
                           'smoke', 'drink',
                           'subscription_purchased', 'subscription_purchased_at', 'subscription'])
        from_id = User.objects.filter(is_superuser=True)[0].id
        from_user_id = RegisterUser.objects.get(id=from_id)
        from_user_name = from_user_id.first_name
        phone_number = self.request.data['phone_number']
        to_user = RegisterUser.objects.get(id=phone_number)
        first_name = to_user.first_name
        to_id = self.request.data['phone_number']
        to_user_id = RegisterUser.objects.get(id=to_id)
        InAppNotification.objects.create(
            from_user_id=from_user_id,
            from_user_name=from_user_name,
            to_user_id=to_user_id,
            to_user_name=first_name,
            notification_type="Profile Update",
            notification_title="Profile Update",
            notification_body="Your profile has been updated"
        )

        return Response({"Profile update successfully"}, status=HTTP_200_OK)


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
    permission_classes = (IsAuthenticated)
    serializer_class = UserInstagramSerializer

    def post(self, request, *args, **kwargs):
        phone_number = self.request.data['id']
        p_no = RegisterUser.objects.get(id=phone_number)
        insta_pic_1 = self.request.data['insta_pic_1']
        insta_pic_2 = self.request.data['insta_pic_2']
        insta_pic_3 = self.request.data['insta_pic_3']
        insta_pic_4 = self.request.data['insta_pic_4']
        insta_pic_5 = self.request.data['insta_pic_5']
        insta_pic_6 = self.request.data['insta_pic_6']
        insta_pic_7 = self.request.data['insta_pic_7']
        insta_pic_8 = self.request.data['insta_pic_8']
        insta_pic_9 = self.request.data['insta_pic_9']
        insta_pic_10 = self.request.data['insta_pic_10']
        UserInstagramPic.objects.create(
            phone_number=p_no,
            insta_pic_1=insta_pic_1,
            insta_pic_2=insta_pic_2,
            insta_pic_3=insta_pic_3,
            insta_pic_4=insta_pic_4,
            insta_pic_5=insta_pic_5,
            insta_pic_6=insta_pic_6,
            insta_pic_7=insta_pic_7,
            insta_pic_8=insta_pic_8,
            insta_pic_9=insta_pic_9,
            insta_pic_10=insta_pic_10,
            insta_connect=True
        )
        return Response({"Success": "Images uploaded from instagram successfully"},
                        status=HTTP_201_CREATED)


class ShowInstagramPics(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = ShowInstaPics

    def get(self, request, *args, **kwargs):
        id = self.request.GET.get('phone_number')
        try:
            pics = UserInstagramPic.objects.get(phone_number=id)
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
                pics = {
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
                }
            return Response({"pics": pics}, status=HTTP_200_OK)
        except:
            return Response({"No instagram pics"}, status=HTTP_400_BAD_REQUEST)


class UserslistAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        # queryset needed to be filtered
        logged_in_user_id = self.request.GET.get('id')
        # queryset1 = RegisterUser.objects.all().exclude(id=logged_in_user_id).values()
        users = []
        # for obj in queryset1:
        #     users.append(obj)
        # return Response({"Users":users}, HTTP_200_OK)
        if (UserDetail.objects.all().exclude(id=logged_in_user_id)).count() > 0:
            for obj in UserDetail.objects.all().exclude(id=logged_in_user_id):
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
                interests = obj.phone_number.interests
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
                if obj.phone_number.pic_7:
                    pic_7 = obj.phone_number.pic_7.url
                else:
                    pic_7 = ''
                if obj.phone_number.pic_8:
                    pic_8 = obj.phone_number.pic_8.url
                else:
                    pic_8 = ''
                if obj.phone_number.pic_9:
                    pic_9 = obj.phone_number.pic_9.url
                else:
                    pic_9 = ''
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
                    "interests": interests,
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
                    "pic_7": pic_7,
                    "pic_8": pic_8,
                    "pic_9": pic_9,
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
                    "fav_pet": fav_pet,
                    "smoke": smoke,
                    "drink": drink,
                    "subscription_purchased": subscription_purchased,
                    "subscription_purchased_at": subscription_purchased_at,
                    # "subscription": subscription
                }
                users.append(detail)
            return Response(users, HTTP_200_OK)
        else:
            return Response({"There are no users"}, status=HTTP_200_OK)


class UserDetailAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = UserDetail
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        phone_number = self.request.GET.get('id')
        # queryset = UserDetail.objects.filter(id=phone_number).values()
        queryset = UserDetail.objects.filter(id=phone_number)
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
            interests = obj.phone_number.interests
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
            if obj.phone_number.pic_7:
                pic_7 = obj.phone_number.pic_7.url
            else:
                pic_7 = ''
            if obj.phone_number.pic_8:
                pic_8 = obj.phone_number.pic_8.url
            else:
                pic_8 = ''
            if obj.phone_number.pic_9:
                pic_9 = obj.phone_number.pic_9.url
            else:
                pic_9 = ''
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
                "pic_7": pic_7,
                "pic_8": pic_8,
                "pic_9": pic_9,
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
                "subscription_purchased_at": subscription_purchased_at,
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


# class SearchUser(ListCreateAPIView):
#     model = RegisterUser
#     serializer_class = RegisterSerializer
#     filter_backends = (rest_framework.DjangoFilterBackend,)
#     filterset_class = SnippetFilter
#     queryset = RegisterUser.objects.all()

# def get_queryset(self):
#     queryset = RegisterUser.objects.all()
#     print(self.request.data)
#     qualification = self.request.GET.get('qualification', None)
#     relationship_status = self.request.GET.get('relationship_status', None)
#     religion = self.request.GET.get('religion', None)
#     body_type = self.request.GET.get('body_type', None)
#     gender = self.request.GET.get('gender', None)
#     interests = self.request.GET.get('interests', None)
# relationship_status = self.request.data['relationship_status']
# religion = self.request.data['religion']
# body_type = self.request.data['body_type']
# gender = self.request.data['gender']
# interests = self.request.data['interests']
# print('Qualification ', qualification)
# if qualification is not None:
# queryset = RegisterUser.objects.filter(Q(qualification__exact=qualification) |
#                                        Q(relationship_status__exact=relationship_status) |
#                                        Q(interests__exact=interests) |
#                                        Q(gender__exact=gender) |
#                                        Q(religion__exact=religion) |
#                                        Q(body_type__exact=body_type)
#                                        )
# print('>>>>>>>>>>>>>>>>>>>>', queryset)
# return queryset

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
        logged_in_user_id = self.request.data['id']
        users_liked_by_me = MatchedUser.objects.filter(
            liked_by_me=logged_in_user_id)
        users_liked_by_me_list = []
        for obj in users_liked_by_me:
            y = obj.user.id
            users_liked_by_me_list.append(y)
        liked_by_me = self.request.data['liked_by_me']

        if int(liked_by_me) not in users_liked_by_me_list:
            register_user = RegisterUser.objects.get(id=logged_in_user_id)
            from_user_name = register_user.first_name
            user = MatchedUser.objects.create(user=register_user, matched='No')
            user.liked_by_me.add(liked_by_me)
            to_user_id = RegisterUser.objects.get(id=liked_by_me)
            to_user_name = to_user_id.first_name
            InAppNotification.objects.create(
                from_user_id=register_user,
                from_user_name=from_user_name,
                to_user_id=to_user_id,
                to_user_name=to_user_name,
                notification_type='Like Notification',
                notification_title='Like Notification',
                notification_body="You have been liked by " + from_user_name
            )
            return Response({"You have liked a user"}, status=HTTP_200_OK)
        else:
            liked_by_me = self.request.data['liked_by_me']
            register_user = RegisterUser.objects.get(id=logged_in_user_id)
            from_user_name = register_user.first_name
            user = MatchedUser.objects.create(
                user=register_user, matched='Yes')
            user.liked_by_me.add(liked_by_me)
            to_user_id = RegisterUser.objects.get(id=liked_by_me)
            to_user_name = to_user_id.first_name
            InAppNotification.objects.create(
                from_user_id=register_user,
                from_user_name=from_user_name,
                to_user_id=to_user_id,
                to_user_name=to_user_name,
                notification_type='Match Notification',
                notification_title='Match Notification',
                notification_body="You have been matched with  " + from_user_name
            )
            return Response({"You have matched with a user"}, status=HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class SuperLikeUserAPIView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = SuperLikeSerializer

    def post(self, request, *args, **kwargs):
        logged_in_user_id = self.request.data['id']
        users_super_liked_me = MatchedUser.objects.filter(
            super_liked_by_me=logged_in_user_id)
        users_super_liked_me_list = []
        for obj in users_super_liked_me:
            y = obj.user.id
            users_super_liked_me_list.append(y)
        super_liked_by_me = self.request.data['super_liked_by_me']
        if int(super_liked_by_me) not in users_super_liked_me_list:
            register_user = RegisterUser.objects.get(id=logged_in_user_id)
            from_user_name = register_user.first_name
            user = MatchedUser.objects.create(
                user=register_user, super_matched='No')
            user.super_liked_by_me.add(super_liked_by_me)
            to_user_id = RegisterUser.objects.get(id=super_liked_by_me)
            to_user_name = to_user_id.first_name
            InAppNotification.objects.create(
                from_user_id=register_user,
                from_user_name=from_user_name,
                to_user_id=to_user_id,
                to_user_name=to_user_name,
                notification_type='Like Notification',
                notification_title='Like Notification',
                notification_body="You have been super liked by " + from_user_name
            )
            return Response({"You have super liked a user"}, status=HTTP_200_OK)
        else:
            super_liked_by_me = self.request.data['super_liked_by_me']
            register_user = RegisterUser.objects.get(id=logged_in_user_id)
            from_user_name = register_user.first_name
            user = MatchedUser.objects.create(
                user=register_user, super_matched='Yes')
            user.super_liked_by_me.add(super_liked_by_me)
            to_user_id = RegisterUser.objects.get(id=super_liked_by_me)
            to_user_name = to_user_id.first_name
            InAppNotification.objects.create(
                from_user_id=register_user,
                from_user_name=from_user_name,
                to_user_id=to_user_id,
                to_user_name=to_user_name,
                notification_type='Match Notification',
                notification_title='Match Notification',
                notification_body="You have  matched with  " + from_user_name
            )
            return Response({"You have super matched with a user"}, status=HTTP_200_OK)


class GetMatchesAPIView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = MatchedUser
    serializer_class = MatchedUserSerializer

    def get(self, request, *args, **kwargs):
        user_id = self.request.data['user_id']
        liked_me = MatchedUser.objects.filter(
            liked_by_me=user_id).exclude(user=user_id).distinct()
        liked_me_list = [obj.user.first_name for obj in liked_me]
        liked_by_me = MatchedUser.objects.filter(user=user_id).distinct()
        liked_by_me_list = []
        for obj in liked_by_me:
            y = obj.liked_by_me.all()
            for z in y:
                liked_by_me_list.append(z.first_name)
        super_liked_me = MatchedUser.objects.filter(
            super_liked_by_me=user_id).exclude(user=user_id).distinct()
        super_liked_by_me = MatchedUser.objects.filter(user=user_id).distinct()
        super_liked_me_list = [x.user.first_name for x in super_liked_me]
        super_liked_by_me_list = []
        for obj in super_liked_by_me:
            y = obj.super_liked_by_me.all()
            for z in y:
                super_liked_by_me_list.append(z.first_name)
        match = []
        super_match = []
        x = set(liked_by_me_list) & set(liked_me_list)
        match.append(x)
        y = set(super_liked_me_list) & set(super_liked_by_me_list)
        super_match.append(y)
        return Response({"Matches": match, "Super Matches": super_match}, status=HTTP_200_OK)


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
            InAppNotification.objects.create(
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

        InAppNotification.objects.create(
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
        phone_number = self.request.data['phone_number']
        logged_in_user_id = self.request.data['id']
        requested_user = RegisterUser.objects.get(id=phone_number)
        scheduled_by = RegisterUser.objects.get(id=logged_in_user_id)
        meeting_date = self.request.data['meeting_date']
        meeting_time = self.request.data['meeting_time']
        venue = self.request.data['venue']
        description = self.request.data['description']
        status = self.request.data['status']
        from_id = logged_in_user_id
        from_user_id = RegisterUser.objects.get(id=from_id)
        from_user_name = from_user_id.first_name
        phone_number = self.request.data['phone_number']
        to_user = RegisterUser.objects.get(id=phone_number)
        first_name = to_user.first_name
        to_id = self.request.data['phone_number']
        to_user_id = RegisterUser.objects.get(id=to_id)
        if logged_in_user_id.gender == 'Female':
            ScheduleMeeting.objects.create(
                scheduled_with=requested_user,
                scheduled_by=scheduled_by,
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                venue=venue,
                description=description,
                status=status
            )
            InAppNotification.objects.create(
                from_user_id=from_user_id,
                from_user_name=from_user_name,
                to_user_id=to_user_id,
                to_user_name=first_name,
                notification_type='Meeting Schedule',
                notification_title='Meeting Schedule Request',
                notification_body='You have a meeting scheduled with ' + from_user_name
            )
            return Response({"Meeting schedule sent successfully"}, status=HTTP_200_OK)
        else:
            return Response({"Only females are allowed to sent meeting request"}, status=HTTP_400_BAD_REQUEST)


class FeedbackApiView(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Feedback
    serializer_class = FeedbackSerializer


class ContactUsApiView(ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = ContactUs
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()


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
                return Response({"Token": user_with_token.key, "user id": user.id, "status": HTTP_200_OK})
        except:
            print('inside except')
            print('Email fb except------------>>>', self.request.data)
            serializer = FacebookSerializer(data=request.data)
            if serializer.is_valid():
                reg_usr = RegisterUser.objects.create(
                    email=email,
                    first_name=name
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
                    phone_number=reg_usr
                )
                token = Token.objects.create(user=user)
                return Response({"Token": token.key, "user id": user.id, "status": HTTP_200_OK})
            else:
                return Response({"message": serializer.errors, "status": HTTP_400_BAD_REQUEST})


class GoogleSignupView(CreateAPIView):
    serializer_class = GmailSerializer

    def post(self, request, *args, **kwargs):
        name = self.request.POST.get('name' or None)
        # last_name = self.request.POST.get('last_name' or None)
        email = self.request.POST.get('email' or None)
        social_id = self.request.POST.get('social_id' or None)
        social_type = self.request.POST.get('social_type' or None)
        device_token = self.request.POST.get('device_token' or None)
        profile_pic = self.request.POST.get('profile_pic' or None)
        try:
            print('Gmail try---------------->', self.request.data)
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
                return Response({"Token": user_with_token.key, "user id": existing_user.id, "status": HTTP_200_OK})
        except:
            print('Gmail except ----------------->>>>>>>>>>>', self.request.data)
            serializer = GmailSerializer(data=request.data)
            if serializer.is_valid():
                reg_usr = RegisterUser.objects.create(
                    email=email,
                    first_name=name
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
                    phone_number=reg_usr
                )
                token = Token.objects.create(user=user)
                return Response({"Token": token.key, "user id": user.id, "status": HTTP_200_OK})
            else:
                return Response({"message": serializer.errors, "status": HTTP_400_BAD_REQUEST})


class CheckNumber(APIView):
    model = User

    def get(self, request, *args, **kwargs):
        phone_number = self.request.GET.get('phone_number')
        try:
            user = User.objects.get(phone_number=phone_number)
            if user:
                return Response({'message': 'User already registered with this number', "status": HTTP_200_OK})
            else:
                return Response({'message': 'User not found', "status": HTTP_400_BAD_REQUEST})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], "status": HTTP_400_BAD_REQUEST})


class PopNotificationAPIView(CreateAPIView):
    serializer_class = PopUpNotificationSerializer

    def post(self, request, *args, **kwargs):
        return Response({"You have updated your meeting status successfully"}, status=HTTP_200_OK)


class SubscriptionPlanAPIView(ListAPIView):
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlans.objects.all()

    # def get(self, request, *args, **kwargs):
    #     queryset = SubscriptionPlans.objects.all().values()
    #     return Response(queryset)
    #
    # def post(self, request, *args, **kwargs):
    #     return Response({"You have updated your meeting request successfully"}, status=HTTP_200_OK)


# class GetScheduledMeeting(APIView):
#
#     def get(self, request, *args, **kwargs):
#         liked_obj = MatchedUser.objects.filter(matched='Yes')
#         for obj in liked_obj:
#             print('<<<<<--------->>>>', obj.user)
#             print('--------->>>>', obj.liked_by_me.all()[0])
#             liked_by = RegisterUser.objects.get(id=obj.user.id)
#             liked_user = RegisterUser.objects.get(id=obj.liked_by_me.all()[0].id)
#             print('...........................', obj.matched_at.date())
#             print('>>>>>>>>>>>>>>>', liked_by.first_name)
#             print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<,', liked_user.first_name)
#             schedule_obj = ScheduleMeeting.objects.filter(
#                 Q(scheduled_by__exact=obj.user.id) & Q(scheduled_with__exact=obj.liked_by_me.all()[0].id) & Q(
#                     status__icontains='Not Completed')).values()
#             if schedule_obj:
#                 for s_obj in schedule_obj:
#                     meeting_at = s_obj['created_at']
#                     m_date = str(meeting_at.date()).split('-')
#                     meeting_year = int(m_date[0])
#                     meeting_month = int(m_date[1])
#                     meeting_date = int(m_date[2])
#                     meeting_at = date(meeting_year, meeting_month, meeting_date)
#                     matched_at = str(obj.matched_at.date()).split('-')
#                     matched_year = int(matched_at[0])
#                     matched_month = int(matched_at[1])
#                     matched_date = int(matched_at[2])
#                     matched_at = date(matched_year, matched_month, matched_date)
#                     delta = matched_at - meeting_at
#                     print(delta.days)
#                     if delta.days > 30:
#                         obj.delete()
#                         return Response({"Objects": schedule_obj}, status=HTTP_200_OK)

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
