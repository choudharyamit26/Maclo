from rest_framework import serializers
# from .models import CustomUser
from django.contrib.auth.models import User

#
# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(
#         style={'input_type': 'password'},
#         trim_whitespace=False
#     )
#     confirm_password = serializers.CharField(
#
#         style={'input_type': 'password'},
#         trim_whitespace=False
#     )
#
#     class Meta:
#         model = User
#         fields = ('email', 'password', 'confirm_password')
#
#
# class LoginSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(style={'input_type': 'password'},
#                                      trim_whitespace=False)
#
#     class Meta:
#         model = User
#         fields = ('email', 'password')


from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

        def create(self, validated_data):
            """Create a new user with encrypted password and return it """
            return get_user_model().objects.create_user(**validated_data)

        def update(self, insatnce, validated_data):
            """Update a user, setting the password corecttly and return it"""
            password = validated_data.pop('password', None)
            user = super().update(insatnce, validated_data)

            if password:
                user.ser_paasword(password)
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
