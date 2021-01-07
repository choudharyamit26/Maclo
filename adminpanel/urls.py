from django.urls import path
from .views import Login, Dashboard, UsersList, UserDetailView, UserDelete, PasswordChangeView, PasswordChangeDoneView, \
    SendNotification
from django.conf import settings
from django.conf.urls.static import static

app_name = 'adminpanel'
urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('users-list/', UsersList.as_view(), name='users-list'),
    path('users-detail/<int:pk>/', UserDetailView.as_view(), name='users-detail'),
    path('user-delete/<int:pk>/', UserDelete.as_view(), name='user-delete'),
    path('change-password/', PasswordChangeView.as_view(template_name='change_password.html'), name='change_password'),
    path('password-change-done/', PasswordChangeDoneView.as_view(template_name='change_password_done.html'),
         name='password_change_done'),
    path('send-notification/', SendNotification.as_view(),
         name='send-notification'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
