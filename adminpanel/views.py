# from django.shortcuts import render
# from django.contrib.auth import get_user_model, login
# from django.contrib.auth.hashers import make_password
# from rest_framework.generics import CreateAPIView
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_401_UNAUTHORIZED
# # from adminpanel.models import CustomUser
# from adminpanel.serializers import UserSerializer, LoginSerializer
#
# User = get_user_model()
#
#
# class CreateUserView(CreateAPIView):
#     model = User
#     serializer_class = UserSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = UserSerializer(data=self.request.data)
#         email = self.request.data['email']
#         password = self.request.data['password']
#         confirm_password = self.request.data['confirm_password']
#         user_qs = User.objects.filter(email__iexact=email)
#         if user_qs.exists():
#             serializer.is_valid(raise_exception=True)
#             return Response({"Email": "User with this email already exists."}, status=HTTP_200_OK)
#         if password == confirm_password:
#             User.objects.create(
#                 email=email,
#                 password=make_password(password),
#                 confirm_password=make_password(confirm_password),
#                 is_superuser=True
#             )
#             serializer.is_valid(raise_exception=True)
#             return Response({"Created": "User Created successfully"}, status=HTTP_201_CREATED)
#         else:
#             serializer.is_valid(raise_exception=True)
#             return Response({"Passwords": "Password and Confirm Password must match."}, status=HTTP_400_BAD_REQUEST)
#
#
# class LoginAPIView(APIView):
#     # model = User
#     serializer_class = LoginSerializer
#
#     def post(self, request):
#         print(self.request.data)
#         email = self.request.data['email']
#         password = self.request.data['password']
#         try:
#             user_object = User.objects.get(email=email)
#             if user_object.check_password(password):
#                 if user_object.is_superuser:
#                     login(self.request, user_object)
#                     return Response({"Login": "Logged in successfully"}, status=HTTP_200_OK)
#                 else:
#                     return Response({"Not authorised": "You are not authorised"}, status=HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({"Password error": "Incorrect Password"}, status=HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             print(e)
#             return Response({"Email error": "Email doesn't exists"}, status=HTTP_400_BAD_REQUEST)

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import UserSerializer, AuthTokenSerializer
from django.views.decorators.csrf import csrf_exempt


# @csrf_exempt
class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
