from django.urls import path, re_path

from .views import (
    CreateChatroom,
    ChatList,
    MessagesList,
    CheckRoom,
    UnReadMessageCount,
    UpdateUnReadMessage,
    DeleteChatRoom,
    DeleteChatMessages,
    DeleteMessage
)

app_name = 'chat'

urlpatterns = [
    path('create-room/', CreateChatroom.as_view(), name='create-room'),
    path('chat-list/', ChatList.as_view(), name='chat-list'),
    path('messages/', MessagesList.as_view(), name='messages'),
    path('check-room/', CheckRoom.as_view(), name='check-room'),
    path('unread-message-count/', UnReadMessageCount.as_view(), name='unread-message-count'),
    path('update-message/', UpdateUnReadMessage.as_view(), name='update-message'),
    path('delete-chat-room/', DeleteChatRoom.as_view(), name='delete-chat-room'),
    path('delete-chat-messages/', DeleteChatMessages.as_view(), name='delete-chat-messages'),
    path('delete-message/', DeleteMessage.as_view(), name='delete-message'),
]
