from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from .views import (UserCreateAPIView, UserInstagramPicsAPIView, UserDetailAPIView, UserslistAPIView,
                    UserProfileAPIView, SearchUser, GetMatchesAPIView, LikeUserAPIView, DeleteMatchesAPIView,
                    RequestMeetingAPIView, MeetingStatusAPIView, ScheduleMeetingAPIView, FeedbackApiView,
                    ContactUsApiView, AboutUsApiView, EditAboutUsAPIView, EditContactUsApiView, FacebookSignupApiView,
                    GoogleSignupView, UserProfileUpdateView, UpdatePhoneNumber, SuperLikeUserAPIView,GetMediaContent,
                    PopNotificationAPIView, SubscriptionPlanAPIView, DeleteSuperMatchesAPIView,GetUserInstagramPics,ShowInstagramPics)

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
    path('update-phonenumber/<int:pk>/', UpdatePhoneNumber.as_view(), name='update-phonenumber'),
    # path('get-token/',GetUserToken.as_view(),name='get-token'),
    path('user-profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('user-profile-update/<int:pk>/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('get-insta-pics/', GetUserInstagramPics.as_view(), name='get-insta-pics'),
    path('user-insta-pics/', UserInstagramPicsAPIView.as_view(), name='insta-pics'),
    path('show-user-insta-pics/', ShowInstagramPics.as_view(), name='show-insta-pics'),
    path('users-list/', UserslistAPIView.as_view(), name='users-list'),
    path('users-detail/', UserDetailAPIView.as_view(), name='user-detail'),
    path('user-search/', SearchUser.as_view(), name='user-search'),
    path('user-getmatches/', GetMatchesAPIView.as_view(), name='get-matches'),
    path('like-user/', LikeUserAPIView.as_view(), name='like-user'),
    path('superlike-user/', SuperLikeUserAPIView.as_view(), name='superlike-user'),
    path('user-deletematches/', DeleteMatchesAPIView.as_view(), name='delete-match'),
    path('user-deletesupermatches/', DeleteSuperMatchesAPIView.as_view(), name='delete-supermatch'),
    path('request-meeting/', RequestMeetingAPIView.as_view(), name='request-meeting'),
    path('meeting-status/<int:pk>/', MeetingStatusAPIView.as_view(), name='meeting-status'),
    path('schedule-meeting/', ScheduleMeetingAPIView.as_view(), name='schedule-meeting'),
    path('purchase-subscription/', SubscriptionPlanAPIView.as_view(), name='subscription-purchase'),
    path('feedback/', FeedbackApiView.as_view(), name='feedback'),
    path('contactus/', ContactUsApiView.as_view(), name='contactus'),
    path('aboutus/', AboutUsApiView.as_view(), name='aboutus'),
    path('edit-aboutus/', EditAboutUsAPIView.as_view(), name='edit-aboutus'),
    path('edit-contactus/', EditContactUsApiView.as_view(), name='edit-contactus'),
    path('popup-notification/', PopNotificationAPIView.as_view(), name='pop-notification'),
    # path('scheduleobject/', GetScheduledMeeting.as_view(), name='schedule-obj'),
    path('facebook-signup/', FacebookSignupApiView.as_view(), name='fb-signup'),
    path('google-signup/', GoogleSignupView.as_view(), name='google-signup'),
    path('content/', GetMediaContent.as_view(), name='media-content'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
