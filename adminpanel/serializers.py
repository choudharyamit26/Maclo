from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from src.models import RegisterUser


class AdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterUser
        fields = ('email', 'phone_number', 'first_name', 'last_name', 'gender', 'qualification', 'relationship_status',
                  'interests', 'religion', 'body_type')


class AdminFilterSerializer(serializers.ModelSerializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()

    class Meta:
        model = RegisterUser
        fields = ('from_date', 'to_date')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user

# class ChangePasswordSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(write_only=True)
#     new_password = serializers.CharField(write_only=True)
#     old_password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'password', 'old_password', 'new_password', 'confirm_password']
#
#     def update(self, instance, validated_data):
#
#         instance.password = validated_data.get('password', instance.password)
#
#         if not validated_data['new_password']:
#             raise serializers.ValidationError({'new_password': 'not found'})
#
#         if not validated_data['old_password']:
#             raise serializers.ValidationError({'old_password': 'not found'})
#
#         if not instance.check_password(validated_data['old_password']):
#             raise serializers.ValidationError({'old_password': 'wrong password'})
#
#         if validated_data['new_password'] != validated_data['confirm_password']:
#             raise serializers.ValidationError({'passwords': 'passwords do not match'})
#
#         if validated_data['new_password'] == validated_data['confirm_password'] and instance.check_password(
#                 validated_data['old_password']):
#             # instance.password = validated_data['new_password']
#             print(instance.password)
#             instance.set_password(validated_data['new_password'])
#             print(instance.password)
#             instance.save()
#             return instance
#         return instance
