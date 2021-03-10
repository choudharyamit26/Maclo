from django.urls import path
from .views import Login, Dashboard, UsersList, UserDetailView, UserDelete, PasswordChangeView, PasswordChangeDoneView, \
    SendNotification, CreateSubscriptionPlan, SubscriptionsPlansList, PurchasedSubscriptionList, MeetupList, \
    TransactionsList, ReportsView, StaticContentView, PrivacyPolicyUrl, UpdateAboutUs, UpdateContactUs, QueriesList, \
    FeedbackView,PrivacyPolicyView
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
    path('create-subscription-plan/', CreateSubscriptionPlan.as_view(), name='create-subscription-plan'),
    path('subscription-plans-list/', SubscriptionsPlansList.as_view(), name='subscription-plans-list'),
    path('meetup-list/', MeetupList.as_view(), name='meetup-list'),
    path('transactions-list/', TransactionsList.as_view(), name='transactions-list'),
    path('reports/', ReportsView.as_view(), name='reports'),
    path('privacy-policy-url/', PrivacyPolicyUrl.as_view(), name='privacy-policy-url'),
    path('static-content/', StaticContentView.as_view(), name='static-content'),
    path('update-about-us/<int:pk>/', UpdateAboutUs.as_view(), name='update-about-us'),
    path('update-contact-us/<int:pk>/', UpdateContactUs.as_view(), name='update-contact-us'),
    path('purchased-subscription-plans-list/', PurchasedSubscriptionList.as_view(),
         name='purchased-subscription-plans-list'),
    path('query-list/', QueriesList.as_view(), name='query-list'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
