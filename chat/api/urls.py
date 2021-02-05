from django.urls import path, re_path

from .views import (
    CreateChatroom,
    ChatList,
    MessagesList,
    CheckRoom
)

app_name = 'chat'

urlpatterns = [
    path('create-room/', CreateChatroom.as_view(), name='create-room'),
    path('chat-list/', ChatList.as_view(), name='chat-list'),
    path('messages/', MessagesList.as_view(), name='messages'),
    path('check-room/', CheckRoom.as_view(), name='check-room')
]
