from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from chat.models import ChatRoom, Message
from chat.views import get_user_contact
from .serializers import ChatSerializer
from src.models import RegisterUser, BlockedUsers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

User = RegisterUser()


class CreateChatroom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        sender = self.request.POST['sender']
        receiver = self.request.POST['receiver']
        sender_obj = RegisterUser.objects.get(id=sender)
        receiver_obj = RegisterUser.objects.get(id=receiver)
        chat_room = ChatRoom.objects.create(
            sender=sender_obj,
            receiver=receiver_obj
        )

        return Response({'room_id': chat_room.id, 'status': HTTP_200_OK})


class MessagesList(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        room_id = self.request.query_params.get('room_id')
        chat = ChatRoom.objects.get(id=room_id)
        messages = []
        for message in chat.messages.all():
            messages.append({'id': message.id, 'sender': message.sender.id, 'receiver': message.receiver.id,
                             'message': message.message, 'is_image': message.is_image,
                             'created_at': str(message.created_at.replace(microsecond=0))})
        return Response({'messages': messages, 'status': HTTP_200_OK})


class ChatList(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        user_id = self.request.user
        r_user = RegisterUser.objects.get(email=user_id.email)
        sender_chat = ChatRoom.objects.filter(sender=r_user)
        receiver_chat = ChatRoom.objects.filter(receiver=r_user)
        rooms = sender_chat | receiver_chat
        users_blocked_by_me = BlockedUsers.objects.filter(user=r_user)
        print('USERS BLOCKED BY ME ', users_blocked_by_me)
        # users_blocked_by_me_list_2 = [x for x in users_blocked_by_me for y in x.blocked.all()]
        # print('BLOCKED LIST 2', users_blocked_by_me_list_2)
        users_blocked_by_me_list = []
        for user in users_blocked_by_me:
            for u in user.blocked.all():
                users_blocked_by_me_list.append(u.id)
        print('USERS BLOCKED BY ME LIST---', users_blocked_by_me_list)
        users_blocked_me = BlockedUsers.objects.filter(blocked=r_user)
        print('USERS BLOCKED ME ID', [x.user.id for x in users_blocked_me])
        # users_blocked_me_list = [x.id for x in users_blocked_me.blocked.all()]
        users_blocked_me_list = []
        for user in users_blocked_me:
            users_blocked_me_list.append(user.user.id)
        print('USERS BLOCKED ME ', users_blocked_me_list)
        final_blocked_users_list = users_blocked_by_me_list + users_blocked_me_list
        print('FINAL BLOCKED LIST', final_blocked_users_list)
        print(rooms.order_by('-created_at').values())
        sent_massage = []
        received_message = []
        for message in sender_chat:
            if RegisterUser.objects.get(id=message.sender_id).pic_1 and RegisterUser.objects.get(
                    id=message.receiver_id).pic_1:
                if message.messages.last():
                    if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': False})
            elif RegisterUser.objects.get(id=message.sender_id).pic_1:
                if message.messages.last():
                    if message.sender.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.sender.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': False})

            elif RegisterUser.objects.get(id=message.receiver_id).pic_1:
                if message.messages.last():
                    if message.sender.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.sender.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': False})
            else:
                if message.messages.last():
                    if message.sender.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.sender.id in final_blocked_users_list:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        sent_massage.append(
                            {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': False})
        for message in receiver_chat:
            if RegisterUser.objects.get(id=message.sender_id).pic_1 and RegisterUser.objects.get(
                    id=message.receiver_id).pic_1:
                if message.messages.last():
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': False})
            elif RegisterUser.objects.get(id=message.sender_id).pic_1:
                if message.messages.last():
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                             'last_message': '',
                             'created_at': '', 'blocked': False})
            elif RegisterUser.objects.get(id=message.receiver_id).pic_1:
                if message.messages.last():
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': False})
            else:
                if message.messages.last():
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': message.messages.last().message,
                             'created_at': str(message.messages.last().created_at), 'blocked': False})
                else:
                    if message.receiver.id in final_blocked_users_list:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': True})
                    else:
                        received_message.append(
                            {'id': message.id, 'sender': message.receiver.id, 'sender_name': RegisterUser.objects.get(
                                id=message.receiver_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.receiver_id).last_name,
                             'sender_profile_pic': '',
                             'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                id=message.sender_id).last_name,
                             'receiver_profile_pic': '',
                             'last_message': '',
                             'created_at': '', 'blocked': False})
        return Response({'messages': sent_massage + received_message, 'status': HTTP_200_OK})


class CheckRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        sender_id = self.request.query_params.get('sender')
        receiver_id = self.request.query_params.get('receiver')
        sender = RegisterUser.objects.get(id=sender_id)
        receiver = RegisterUser.objects.get(id=receiver_id)
        try:
            try:
                room = ChatRoom.objects.get(sender=sender, receiver=receiver)
                return Response({'room_exists': True, 'room_id': room.id, 'status': HTTP_200_OK})
            except Exception as e:
                room = ChatRoom.objects.get(sender=receiver, receiver=sender)
                return Response({'room_exists': True, 'room_id': room.id, 'status': HTTP_200_OK})
        except Exception as e:
            print(e)
            return Response({'room_exists': False, 'room_id': '', 'status': HTTP_400_BAD_REQUEST})
