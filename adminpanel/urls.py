from django.urls import path
from .views import CreateUserView, Login, ChangePasswordView, DashboardHomeAPIView, SearchUserApiView, AdminFilter, \
    GetUserDetail, UpdateUserDetail, DeleteUserAPIView, CreateSubscriptionPlan

app_name = 'adminpanel'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create-user'),
    path('login/', Login.as_view(), name='login'),
    path('change-password/<int:pk>/', ChangePasswordView.as_view(), name='change-password'),
    path('home/', DashboardHomeAPIView.as_view(), name='dashboard-home'),
    path('search/', SearchUserApiView.as_view(), name='admin-search'),
    path('filter/', AdminFilter.as_view(), name='admin-filter'),
    path('user-detail/', GetUserDetail.as_view(), name='user-detail-admin'),
    path('update-user-detail/<int:pk>', UpdateUserDetail.as_view(), name='update-user-detail-admin'),
    path('delete-user/<int:pk>', DeleteUserAPIView.as_view(), name='delete-user-admin'),
    path('create-subscription/', CreateSubscriptionPlan.as_view(), name='create-subscription')
]
