from rest_framework import serializers
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from .models import UserDetail, UserInstagramPic, RegisterUser, MatchedUser, RequestMeeting, ScheduleMeeting, Feedback, \
    ContactUs, AboutUs, SubscriptionPlans, PopNotification
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUser
        fields = '__all__'


class SocialUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUser
        exclude = ('phone_number',)


class ShowInstaPics(serializers.ModelSerializer):
    class Meta:
        model = UserInstagramPic
        fields = ('phone_number',)


# class UserCreateSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField()
#     phone_number = serializers.CharField()
#     first_name = serializers.CharField()
#     last_name = serializers.CharField()
#     gender = serializers.CharField()
#     date_of_birth = serializers.DateField()
#     job_profile = serializers.CharField()
#     company_name = serializers.CharField()
#     qualification = serializers.CharField()
#     relationship_status = serializers.CharField()
#     interests = serializers.CharField()
#     religion = serializers.CharField()
#     body_type = serializers.CharField()
#     created_at = serializers.CharField(default=timezone.now())
#     fav_quote = serializers.CharField()
#     verified = serializers.CharField(default='No')
#     fb_signup = serializers.CharField(default='No')
#     pic1 = serializers.ImageField(allow_null=True)
#     pic2 = serializers.ImageField(allow_null=True)
#     pic3 = serializers.ImageField(allow_null=True)
#     pic4 = serializers.ImageField(allow_null=True)
#     pic5 = serializers.ImageField(allow_null=True)
#     pic6 = serializers.ImageField(allow_null=True)
#     pic7 = serializers.ImageField(allow_null=True)
#     pic8 = serializers.ImageField(allow_null=True)
#     pic9 = serializers.ImageField(allow_null=True)

#     class Meta:
#         model = User
#         fields = (
#             'email', 'phone_number', 'first_name', 'last_name', 'gender', 'date_of_birth', 'created_at', 'job_profile',
#             'company_name', 'religion', 'qualification', 'relationship_status', 'interests', 'religion', 'body_type',
#             'verified', 'fb_signup', 'fav_quote', 'pic1', 'pic2', 'pic3', 'pic4', 'pic5', 'pic6', 'pic7', 'pic8',
#             'pic9')

#     def create(self, validated_data):
#         email = validated_data['email']
#         phone_number = validated_data['phone_number']
#         first_name = validated_data['first_name']
#         last_name = validated_data['last_name']
#         gender = validated_data['gender']
#         date_of_birth = validated_data['date_of_birth']
#         job_profile = validated_data['job_profile']
#         company_name = validated_data['company_name']
#         qualification = validated_data['qualification']
#         relationship_status = validated_data['relationship_status']
#         interests = validated_data['interests']
#         religion = validated_data['religion']
#         body_type = validated_data['body_type']
#         created_at = validated_data['created_at']
#         verified = validated_data['verified']
#         fb_signup = validated_data['fb_signup']
#         pic1 = validated_data['pic1']
#         pic2 = validated_data['pic2']
#         pic3 = validated_data['pic3']
#         pic4 = validated_data['pic4']
#         pic5 = validated_data['pic5']
#         pic6 = validated_data['pic6']
#         pic7 = validated_data['pic7']
#         pic8 = validated_data['pic8']
#         pic9 = validated_data['pic9']

#         userObj = User(email=email, name=first_name)
#         userObj.save()
#         register_user = RegisterUser.objects.filter(phone_number=phone_number)
#         if register_user:
#             return Response ({"User with this phone number already exists"},status=HTTP_400_BAD_REQUEST)
#         else:
#             RegisterUser.objects.create(
#                 user=userObj,
#                 email=email,
#                 phone_number=phone_number,
#                 first_name=first_name,
#                 last_name=last_name,
#                 gender=gender,
#                 date_of_birth=date_of_birth,
#                 job_profile=job_profile,
#                 company_name=company_name,
#                 qualification=qualification,
#                 relationship_status=relationship_status,
#                 interests=interests,
#                 religion=religion,
#                 body_type=body_type,
#                 created_at=created_at,
#                 verified=verified,
#                 fb_signup=fb_signup,
#                 pic_1=pic1,
#                 pic_2=pic2,
#                 pic_3=pic3,
#                 pic_4=pic4,
#                 pic_5=pic5,
#                 pic_6=pic6,
#                 pic_7=pic7,
#                 pic_8=pic8,
#                 pic_9=pic9
#             )
#         # if User.email.exists():
#         #     print(User.email.exists())
#         #     return Response({"User with this email already exists"}, status=HTTP_400_BAD_REQUEST)
#         return validated_data


# class GetUserTokenSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RegisterUser
#         fields = ('phone_number',)


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUser
        fields = ('qualification', 'relationship_status',
                  'religion', 'body_type', 'interests', 'gender')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'


class UserInstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInstagramPic
        fields = (
            'phone_number', 'insta_pic_1', 'insta_pic_2', 'insta_pic_3', 'insta_pic_4', 'insta_pic_5', 'insta_pic_6',
            'insta_pic_7', 'insta_pic_8', 'insta_pic_9', 'insta_pic_10',)


class MatchedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = ('liked_by_me',)


class SuperLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = ('super_liked_by_me',)


class DeleteMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = ('liked_by_me',)


class DeleteSuperMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = ('super_liked_by_me',)


class RequestMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMeeting
        fields = ('phone_number',)


class MeetingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMeeting
        fields = '__all__'


class ScheduleMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleMeeting
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('phone_number', 'feedback')


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlans
        # fields = '__all__'
        exclude = ("valid_till",)


class PopUpNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopNotification
        fields = '__all__'


class GetInstagramPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInstagramPic
        fields = ('username', 'password')
