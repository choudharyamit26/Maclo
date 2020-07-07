from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import UpdateAPIView, CreateAPIView, ListAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from src.models import RegisterUser, SubscriptionPlans, ScheduleMeeting, UserDetail
from src.serializers import RegisterSerializer, SubscriptionPlanSerializer
from .serializers import UserSerializer, AuthTokenSerializer, ChangePasswordSerializer, AdminRegisterSerializer, \
    AdminFilterSerializer

User = get_user_model()


# @csrf_exempt
class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the system"""
    serializer_class = UserSerializer


class Login(ObtainAuthToken):
    """Create a new token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class PasswordResetConfirmView(APIView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = User.objects.get(id=uid)
        token_generator = default_token_generator
        if token_generator.check_token(user_object, token):
            return render(request, 'password_reset_confirm.html')
        else:
            # messages.error(request, "Link is Invalid")
            # return render(request, 'password_reset_confirm.html')
            return Response({"Invalid link": "LInk is invalid"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):

        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = User.objects.get(id=uid)
        token_generator = default_token_generator
        if not token_generator.check_token(user_object, token):
            # messages.error(self.request, "Link is Invalid")
            # return render(request, 'password_reset_confirm.html')
            return Response({"Invalid": "Link is Invalid"}, status=HTTP_400_BAD_REQUEST)
        password1 = self.request.POST.get('new_password1')
        password2 = self.request.POST.get('new_password2')

        if password1 != password2:
            # messages.error(self.request, "Passwords do not match")
            # return render(request, 'password_reset_confirm.html')
            return Response({"Error": "Passwords do not match"}, status=HTTP_400_BAD_REQUEST)
        elif len(password1) < 8:
            # messages.error(self.request, "Password must be atleast 8 characters long")
            return Response({"Error": "Password must be atleast 8 characters long"}, status=HTTP_400_BAD_REQUEST)
        elif password1.isdigit() or password2.isdigit() or password1.isalpha() or password2.isalpha():
            # messages.error(self.request, "Passwords must have a mix of numbers and characters")
            return Response({"Error": "Passwords must have a mix of numbers and characters"},
                            status=HTTP_400_BAD_REQUEST)
        else:
            token = kwargs['token']
            user_id_b64 = kwargs['uidb64']
            uid = urlsafe_base64_decode(user_id_b64).decode()
            user_object = User.objects.get(id=uid)
            user_object.set_password(password1)
            user_object.save()
            # return HttpResponseRedirect('/password-reset-complete/')
            return Response({"Password changed successfully "}, status=HTTP_200_OK)


class PasswordResetView(APIView):
    template_name = 'password_reset.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'password_reset.html')

    def post(self, request, *args, **kwargs):
        user = get_user_model()
        email = request.POST.get('email')
        email_template = "password_reset_email.html"
        user_qs = user.objects.filter(email=email)
        if len(user_qs) == 0:
            # messages.error(request, 'Email does not exists')
            # return render(request, 'password_reset.html')
            return Response({"Error": "Email does not exists"}, status=HTTP_400_BAD_REQUEST)

        elif len(user_qs) == 1:
            user_object = user_qs[0]
            email = user_object.email
            uid = urlsafe_base64_encode(force_bytes(user_object.id))
            token = default_token_generator.make_token(user_object)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            domain = request.META['HTTP_HOST']
            user = user_object
            site_name = "Quant Energy"

            context = {
                "email": email,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
                "user": user,
                "site_name": site_name
            }
            subject = "Reset Password Link"
            email_body = render_to_string(email_template, context)
            send_mail(subject, email_body, DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            return redirect('/password-reset-done/')
        else:

            user_object = user_qs[0]
            email = user_object.email
            uid = urlsafe_base64_encode(force_bytes(user_object.id))
            token = default_token_generator.make_token(user_object)
            if request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            domain = request.META['HTTP_HOST']
            user = user_object
            site_name = "Quant Energy"

            context = {
                "email": email,
                "uid": uid,
                "token": token,
                "protocol": protocol,
                "domain": domain,
                "user": user,
                "site_name": site_name
            }

            subject = "Reset Password Link"
            email_body = render_to_string(email_template, context)
            send_mail(subject, email_body, DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            return redirect('/password-reset-done/')


# @method_decorator(csrf_exempt, name='dispatch')
# class ChangePasswordView(RetrieveUpdateAPIView):
#     queryset = User.objects.all()
#     serializer_class = ChangePasswordSerializer
# permission_classes = [IsAuthenticated]
#
@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(LoginRequiredMixin, UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # if using drf authtoken, create a new token
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token, created = Token.objects.get_or_create(user=user)
        # return new token
        return Response({'token': token.key}, status=HTTP_200_OK)


class DashboardHomeAPIView(APIView):
    serializer_class = RegisterSerializer

    def get(self, request, *args, **kwargs):
        users_count = RegisterUser.objects.all().count()
        subscription_count = SubscriptionPlans.objects.all().count()
        active_meetups = ScheduleMeeting.objects.all().count()
        revenue = [x.amount for x in SubscriptionPlans.objects.all()]
        return Response(
            {"users_count": users_count, "Subscriptions": subscription_count, "active_meetups": active_meetups,
             "revenue": sum(revenue)})


class SearchUserApiView(CreateAPIView):
    model = RegisterUser
    serializer_class = AdminRegisterSerializer

    def post(self, request, *args, **kwargs):
        data = self.request.data
        qualification = self.request.data['qualification']
        relationship_status = self.request.data['relationship_status']
        religion = self.request.data['religion']
        body_type = self.request.data['body_type']
        gender = self.request.data['gender']
        interests = self.request.data['interests']
        email = self.request.data['email']
        phone_number = self.request.data['phone_number']
        first_name = self.request.data['first_name']
        last_name = self.request.data['last_name']
        if data:
            qs = RegisterUser.objects.filter(Q(last_name__exact=last_name) |
                                             Q(first_name__exact=first_name) |
                                             Q(qualification__exact=qualification) |
                                             Q(relationship_status__exact=relationship_status) |
                                             Q(interests__exact=interests) |
                                             Q(gender__exact=gender) |
                                             Q(religion__exact=religion) |
                                             Q(body_type__exact=body_type) |
                                             Q(email__exact=email) |
                                             Q(phone_number__exact=phone_number)
                                             )
            return Response({"Results": qs}, status=HTTP_200_OK)


class AdminFilter(ListAPIView):
    model = RegisterUser
    serializer_class = AdminFilterSerializer
    queryset = RegisterUser.objects.all()

    def post(self, request, *args, **kwargs):
        from_date = self.request.data['from_date']
        to_date = self.request.data['to_date']

        if from_date and to_date:
            data = RegisterUser.objects.filter(Q(created_at__gte=from_date) |
                                               Q(created_at__lte=to_date))
            return Response({"data": data}, status=HTTP_200_OK)
        else:
            return Response({"Please enter a date range"}, status=HTTP_400_BAD_REQUEST)


class GetUserDetail(ListAPIView):
    model = RegisterUser
    serializer_class = RegisterSerializer

    def get_queryset(self):
        user_id = self.request.data['id']
        user_details = RegisterUser.objects.get(id=user_id)
        phone_number = user_details.phone_number
        user_other_info = UserDetail.objects.filter(phone_number=phone_number)
        return Response(user_details, user_other_info)


class UpdateUserDetail(UpdateAPIView):
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()


class DeleteUserAPIView(DestroyAPIView):
    serializer_class = RegisterSerializer
    queryset = RegisterUser.objects.all()


class CreateSubscriptionPlan(CreateAPIView):
    serializer_class = SubscriptionPlanSerializer
