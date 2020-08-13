from django.urls import path
from .views import Login, Dashboard,UsersList,UserDetailView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'adminpanel'
urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('users-list/', UsersList.as_view(), name='users-list'),
    path('users-detail/<int:pk>/', UserDetailView.as_view(), name='users-detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)