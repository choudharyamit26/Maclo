from django.urls import path
from .views import CreateUserView, CreateTokenView

app_name = 'adminpanel'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create-user'),
    path('login/', CreateTokenView.as_view(), name='user-login')
]
