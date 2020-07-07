"""maclo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, \
    PasswordResetCompleteView, PasswordChangeDoneView, PasswordChangeView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('src.urls', namespace='api')),
    path('chat/', include('chat.api.urls', namespace='chat')),
    path('adminpanel/', include('adminpanel.urls', namespace='adminpanel')),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-done/', PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    # path('change-password/', PasswordChangeView.as_view(template_name='change_password.html'), name='change-password'),
    # path('password-change-done', PasswordChangeDoneView.as_view(template_name='change_password_done.html'),
    #      name='password_change_done'),

]
