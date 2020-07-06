from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from .views import (UserCreateAPIView, UserInstagramPicsAPIView, UserDetailAPIView, UserslistAPIView,
                    UserProfileAPIView, SearchUser, GetMatchesAPIView, CreateMatchesAPIView, DeleteMatchesAPIView,
                    RequestMeetingAPIView, MeetingStatusAPIView, ScheduleMeetingAPIView, FeedbackApiView,
                    ContactUsApiView, AboutUsApiView, FacebookSignupApiView, GoogleSignupView)

app_name = 'src'

schema_view = get_schema_view(
    openapi.Info(
        title="Maclo  API",
        default_version='v1',
        description="APIs for Maclo Dating App",
        terms_of_service="https://www.maclo.com",
        contact=openapi.Contact(email="maclodatingapp@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('user-create/', UserCreateAPIView.as_view(), name='user-detail'),
    path('user-profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('user-insta-pics/', UserInstagramPicsAPIView.as_view(), name='insta-pics'),
    path('users-list/', UserslistAPIView.as_view(), name='users-list'),
    path('users-detail/', UserDetailAPIView.as_view(), name='user-detail'),
    path('user-search/', SearchUser.as_view(), name='user-search'),
    path('user-getmatches/', GetMatchesAPIView.as_view(), name='get-matches'),
    path('user-creatematches/', CreateMatchesAPIView.as_view(), name='create-matches'),
    path('user-deletematches/', DeleteMatchesAPIView.as_view(), name='delete-match'),
    path('request-meeting/', RequestMeetingAPIView.as_view(), name='request-meeting'),
    path('meeting-status/<int:pk>/', MeetingStatusAPIView.as_view(), name='meeting-status'),
    path('schedule-meeting/', ScheduleMeetingAPIView.as_view(), name='schedule-meeting'),
    path('feedback/', FeedbackApiView.as_view(), name='feedback'),
    path('contactus/', ContactUsApiView.as_view(), name='contactus'),
    path('aboutus/', AboutUsApiView.as_view(), name='aboutus'),
    path('facebook-signup/', FacebookSignupApiView.as_view(), name='fb-signup'),
    path('google-signup/', GoogleSignupView.as_view(), name='google-signup'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
