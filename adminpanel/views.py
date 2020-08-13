from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LoginForm
from src.models import RegisterUser, SubscriptionPlans, ScheduleMeeting, UserDetail
from .filters import UserFilter

user = get_user_model()


class Login(View):
    template_name = 'login.html'
    form_class = LoginForm

    def get(self, request):
        form = LoginForm
        return render(self.request, 'login.html', {'form': form})

    def post(self, request):
        email = self.request.POST['email']
        password = self.request.POST['password']
        remember_me = self.request.POST.get('remember_me' or None)
        try:
            user_object = user.objects.get(email=email)
            if user_object.check_password(password):
                if user_object.is_superuser:
                    login(self.request, user_object)
                    messages.success(self.request, 'Logged in successfully')
                    if not remember_me:
                        self.request.session.set_expiry(0)
                    else:
                        request.session.set_expiry(1209600)
                    return redirect('adminpanel:dashboard')
                else:
                    messages.error(self.request, "You are not authorised")
                    return render(request, 'login.html')
            else:
                messages.error(self.request, "Incorrect Password")
                return render(request, 'login.html')
        except:
            messages.error(self.request, "Email doesn't exists")
            return render(self.request, 'login.html')


class PasswordResetConfirmView(View):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = user.objects.get(id=uid)
        token_generator = default_token_generator
        if token_generator.check_token(user_object, token):
            return render(request, 'password_reset_confirm.html')
        else:
            messages.error(request, "Link is Invalid")
            return render(request, 'password_reset_confirm.html')

    def post(self, request, *args, **kwargs):

        token = kwargs['token']
        user_id_b64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(user_id_b64).decode()
        user_object = user.objects.get(id=uid)
        token_generator = default_token_generator
        if not token_generator.check_token(user_object, token):
            messages.error(self.request, "Link is Invalid")
            return render(request, 'password_reset_confirm.html')

        password1 = self.request.POST.get('new_password1')
        password2 = self.request.POST.get('new_password2')

        if password1 != password2:
            messages.error(self.request, "Passwords do not match")
            return render(request, 'password_reset_confirm.html')
        elif len(password1) < 8:
            messages.error(self.request, "Password must be atleast 8 characters long")
            return render(request, 'password_reset_confirm.html')
        elif password1.isdigit() or password2.isdigit() or password1.isalpha() or password2.isalpha():
            messages.error(self.request, "Passwords must have a mix of numbers and characters")
            return render(request, 'password_reset_confirm.html')
        else:
            token = kwargs['token']
            user_id_b64 = kwargs['uidb64']
            uid = urlsafe_base64_decode(user_id_b64).decode()
            user_object = user.objects.get(id=uid)
            user_object.set_password(password1)
            user_object.save()
            return HttpResponseRedirect('/password-reset-complete/')


class PasswordResetView(View):
    template_name = 'password_reset.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'password_reset.html')

    def post(self, request, *args, **kwargs):
        user = get_user_model()
        print(user)
        email = request.POST.get('email')
        print(email)
        email_template = "password_reset_email.html"
        user_qs = user.objects.filter(email=email)
        if len(user_qs) == 0:
            messages.error(request, 'Email does not exists')
            return render(request, 'password_reset.html')

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
            site_name = "Maclo"

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
            site_name = "Maclo "

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


class Dashboard(LoginRequiredMixin, ListView):
    model = RegisterUser
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        users_count = RegisterUser.objects.all().count()
        subscription_count = SubscriptionPlans.objects.all().count()
        date_time = timezone.now().date()
        # print(date_time.date())
        print(date_time)
        meetups = ScheduleMeeting.objects.filter(meeting_date__gte=date_time).count()
        revenue = None
        context = {
            'users_count': users_count,
            'subscription_count': subscription_count,
            'meetups': meetups,
            'revenue': revenue
        }
        return render(self.request, "dashboard.html", context)


class UsersList(LoginRequiredMixin, ListView):
    paginate_by = 1
    model = RegisterUser
    template_name = 'user-management.html'

    def get(self, request, *args, **kwargs):
        qs = self.request.GET.get('qs')
        if qs:
            search = RegisterUser.objects.filter(Q(first_name__icontains=qs) |
                                                 Q(last_name__icontains=qs) |
                                                 Q(email__icontains=qs) |
                                                 Q(phone_number__icontains=qs) |
                                                 Q(promocode__icontains=qs))

            search_count = len(search)
            context = {
                'search': search,
            }
            if search:
                messages.info(self.request, str(
                    search_count) + ' matches found')
                return render(self.request, 'user-management.html', context)
            else:
                messages.info(self.request, 'No results found')
                return render(self.request, 'user-management.html', context)
        else:
            users = RegisterUser.objects.all()
            myfilter = UserFilter(self.request.GET, queryset=users)
            users = myfilter.qs
            paginator = Paginator(users, self.paginate_by)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'object_list': users,
                'myfilter': myfilter,
                'pages': page_obj
            }
            return render(self.request, "user-management.html", context)


class UserDetailView(DetailView):
    model = RegisterUser
    template_name = 'user-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = RegisterUser.objects.get(id=self.kwargs.get('pk'))
        # print(UserDetail.objects.get(phone_number=user))
        print(user)
        try:

            context['detail'] = UserDetail.objects.get(phone_number=user)
            x = UserDetail.objects.get(phone_number=user)
            print(x.living_in)
        except Exception as e:
            print(e)
        return context
