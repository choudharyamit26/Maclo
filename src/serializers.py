from rest_framework import serializers
from .models import UserDetail, UserInstagramPic, RegisterUser, MatchedUser, RequestMeeting, ScheduleMeeting, Feedback, \
    ContactUs, AboutUs


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUser
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'


class UserInstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInstagramPic
        fields = ('phone_number', 'username', 'password')


class MatchedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = '__all__'


class CreateMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = ('liked_by_me', 'super_liked_by_me')


class DeleteMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedUser
        fields = ('liked_by_me', 'super_liked_by_me')


class RequestMeetingSerializer(serializers.ModelSerializer):
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
