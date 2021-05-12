from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import UserCreateAPIView, UserInstagramPicsAPIView, UserDetailAPIView, UserslistAPIView, UserProfileAPIView, \
    SearchUser, GetMatchesAPIView, LikeUserAPIView, DeleteMatchesAPIView, RequestMeetingAPIView, MeetingStatusAPIView, \
    ScheduleMeetingAPIView, FeedbackApiView, ContactUsApiView, AboutUsApiView, EditAboutUsAPIView, EditContactUsApiView, \
    FacebookSignupApiView, GoogleSignupView, UserProfileUpdateView, UpdatePhoneNumber, SuperLikeUserAPIView, \
    GetMediaContent, PopNotificationAPIView, SubscriptionPlanAPIView, DeleteSuperMatchesAPIView, GetUserInstagramPics, \
    ShowInstagramPics, LoginView, CheckNumber, GetNotificationList, UpdateNotification, DeleteNotification, \
    GetUnreadMessageCount, ContactUsQueryForm, UpdateEmail, UpdateProfilePic, Logout, UpdateProfilePic_1, \
    UpdateProfilePic_2, UpdateProfilePic_3, UpdateProfilePic_4, UpdateProfilePic_5, UpdateProfilePic_6, UpdateInterest, \
    UserLikedList, MeetingDetail, MettingList, UpdateMeetingStatus, UpdateUserLocation, UpdateDistanceRange, \
    UpdateAgeRange, UserAge, FilteredUserView, DislikeUser, DeleteAccount, DeactivateAccountView, CheckMeeting, \
    UnMatchView, BlockUserView, BlockedUsersList, UnBlockUser, CheckDob, CheckEmail, CheckUserBlocked, FCMNotification, \
    LikedUserCount, MeetupPopUs, MeetupStatus, DisconnectWithInstagram, ClearNotification, \
    CheckUserProfileCompleteStatus, UpdateMeeting, ShowProfileToOnlyLikedUsers, GetShowProfileToOnlyLikedUsers, \
    UpdateLookingFor, FeedbackWithoutStar

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
    path('user-create/', UserCreateAPIView.as_view(), name='user-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('update-phonenumber/', UpdatePhoneNumber.as_view(), name='update-phonenumber'),
    path('update-email/', UpdateEmail.as_view(), name='update-email'),
    path('update-profile-pic/', UpdateProfilePic.as_view(), name='update-profile-pic'),
    path('update-interest/', UpdateInterest.as_view(), name='update-interest'),
    path('update-distance-range/', UpdateDistanceRange.as_view(), name='update-distance-range'),
    path('update-age-range/', UpdateAgeRange.as_view(), name='update-age-range'),
    path('update-profile-pic-1/', UpdateProfilePic_1.as_view(), name='update-profile-pic-1'),
    path('update-profile-pic-2/', UpdateProfilePic_2.as_view(), name='update-profile-pic-2'),
    path('update-profile-pic-3/', UpdateProfilePic_3.as_view(), name='update-profile-pic-3'),
    path('update-profile-pic-4/', UpdateProfilePic_4.as_view(), name='update-profile-pic-4'),
    path('update-profile-pic-5/', UpdateProfilePic_5.as_view(), name='update-profile-pic-5'),
    path('update-profile-pic-6/', UpdateProfilePic_6.as_view(), name='update-profile-pic-6'),
    # path('get-token/',GetUserToken.as_view(),name='get-token'),
    path('user-profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('user-profile-update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('get-insta-pics/', GetUserInstagramPics.as_view(), name='get-insta-pics'),
    path('user-insta-pics/', UserInstagramPicsAPIView.as_view(), name='insta-pics'),
    path('show-user-insta-pics/', ShowInstagramPics.as_view(), name='show-insta-pics'),
    path('users-list/', UserslistAPIView.as_view(), name='users-list'),
    path('users-detail/', UserDetailAPIView.as_view(), name='user-detail'),
    path('user-search/', SearchUser.as_view(), name='user-search'),
    path('get-user-matches/', GetMatchesAPIView.as_view(), name='get-user-matches'),
    path('like-user/', LikeUserAPIView.as_view(), name='like-user'),
    path('dislike-user/', DislikeUser.as_view(), name='dislike-user'),
    path('superlike-user/', SuperLikeUserAPIView.as_view(), name='superlike-user'),
    path('user-deletematches/', DeleteMatchesAPIView.as_view(), name='delete-match'),
    path('user-deletesupermatches/', DeleteSuperMatchesAPIView.as_view(), name='delete-supermatch'),
    path('request-meeting/', RequestMeetingAPIView.as_view(), name='request-meeting'),
    path('update-meeting/', UpdateMeeting.as_view(), name='update-meeting'),
    path('meeting-status/<int:pk>/', MeetingStatusAPIView.as_view(), name='meeting-status'),
    path('meeting-detail/', MeetingDetail.as_view(), name='meeting-detail'),
    path('meeting-list/', MettingList.as_view(), name='meeting-list'),
    path('update-meeting-status/', UpdateMeetingStatus.as_view(), name='update-meeting-status'),
    path('update-location/', UpdateUserLocation.as_view(), name='update-location'),
    path('schedule-meeting/', ScheduleMeetingAPIView.as_view(), name='schedule-meeting'),
    path('purchase-subscription/', SubscriptionPlanAPIView.as_view(), name='subscription-purchase'),
    path('feedback/', FeedbackApiView.as_view(), name='feedback'),
    path('feedback-without-star/', FeedbackWithoutStar.as_view(), name='feedback-without-star'),
    path('contactus/', ContactUsApiView.as_view(), name='contactus'),
    path('contactus-form/', ContactUsQueryForm.as_view(), name='contactus-form'),
    path('notification-list/', GetNotificationList.as_view(), name='notification-list'),
    path('users-liked-list/', UserLikedList.as_view(), name='users-liked-list'),
    path('delete-user-notification/', DeleteNotification.as_view(),
         name='delete-user-notification'),
    path('delete-all-notifications/', ClearNotification.as_view(), name='delete-all-notifications'),
    path('update-user-notification/',
         UpdateNotification.as_view(), name='update-user-notification'),
    path('user-unread-message-count/', GetUnreadMessageCount.as_view(), name='user-unread-message-count'),
    path('aboutus/', AboutUsApiView.as_view(), name='aboutus'),
    path('edit-aboutus/', EditAboutUsAPIView.as_view(), name='edit-aboutus'),
    path('edit-contactus/', EditContactUsApiView.as_view(), name='edit-contactus'),
    path('popup-notification/', PopNotificationAPIView.as_view(), name='pop-notification'),
    # path('scheduleobject/', GetScheduledMeeting.as_view(), name='schedule-obj'),
    path('facebook-signup/', FacebookSignupApiView.as_view(), name='fb-signup'),
    path('google-signup/', GoogleSignupView.as_view(), name='google-signup'),
    path('content/', GetMediaContent.as_view(), name='media-content'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('check-number/', CheckNumber.as_view(), name='check-number'),
    path('user-age/', UserAge.as_view(), name='user-age'),
    path('home-or-filter/', FilteredUserView.as_view(), name='home-or-filter'),
    path('delete-account/', DeleteAccount.as_view(), name='delete-account'),
    path('deactivate-account/', DeactivateAccountView.as_view(), name='deactivate-account'),
    path('check-meeting/', CheckMeeting.as_view(), name='check-meeting'),
    path('un-match/', UnMatchView.as_view(), name='un-match'),
    path('block-user/', BlockUserView.as_view(), name='block-user'),
    path('unblock-user/', UnBlockUser.as_view(), name='unblock-user'),
    path('blocked-users-list/', BlockedUsersList.as_view(), name='blocked-users-list'),
    path('check-users-dob/', CheckDob.as_view(), name='check-users-dob'),
    path('check-users-email/', CheckEmail.as_view(), name='check-users-email'),
    path('check-users-blocked/', CheckUserBlocked.as_view(), name='check-users-blocked'),
    path('fcm-notification/', FCMNotification.as_view(), name='fcm-notification'),
    path('like-count/', LikedUserCount.as_view(), name='like-count'),
    path('meetup-popup/', MeetupPopUs.as_view(), name='meetup-popup'),
    path('meetup-popup-update/', MeetupStatus.as_view(), name='meetup-popup-update'),
    path('update-lookingfor/', UpdateLookingFor.as_view(), name='update-lookingfor'),
    path('disconnect-instagram/', DisconnectWithInstagram.as_view(), name='disconnect-instagram'),
    path('update-show-only-to-liked/', ShowProfileToOnlyLikedUsers.as_view(), name='update-show-only-to-liked'),
    path('get-show-only-to-liked/', GetShowProfileToOnlyLikedUsers.as_view(), name='get-show-only-to-liked'),
    path('check-profile-complete-status/', CheckUserProfileCompleteStatus.as_view(),
         name='check-profile-complete-status'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
