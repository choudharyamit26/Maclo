from django.db.models import Count
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from chat.models import ChatRoom, Message
from src.models import RegisterUser, BlockedUsers

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
            sender = None
            receiver = None
            if message.sender:
                sender = message.sender.id
            else:
                sender = ''
            if message.receiver:
                receiver = message.receiver.id
            else:
                receiver = ''
            messages.append({'id': message.id, 'sender': sender, 'receiver': receiver,
                             'message': message.message, 'is_image': message.is_image, 'read': message.read,
                             'cleared_by': message.cleared_by,
                             'created_at': str(message.created_at.replace(microsecond=0))})
        return Response({'messages': messages, 'status': HTTP_200_OK})


class UpdateUnReadMessage(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        # room_id = self.request.query_params.get('room_id')
        room_id = self.request.POST['room_id']
        try:
            chat = ChatRoom.objects.get(id=room_id)
            for message in chat.messages.all():
                if message.read:
                    pass
                else:
                    message.read = True
                    message.save()
            return Response({'message': 'Message updated successfully', 'status': HTTP_200_OK})
        except Exception as e:
            x = {'error': str(e)}
            return Response({'message': x['error'], 'status': HTTP_400_BAD_REQUEST})


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
            try:
                if RegisterUser.objects.get(id=message.sender_id).pic_1 and RegisterUser.objects.get(
                        id=message.receiver_id).pic_1:
                    if message.messages.last():
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
                elif RegisterUser.objects.get(id=message.sender_id).pic_1:
                    if message.messages.last():
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                    id=message.sender_id).last_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name + ' ' + RegisterUser.objects.get(
                                    id=message.sender_id).last_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
                elif RegisterUser.objects.get(id=message.receiver_id).pic_1:
                    if message.messages.last():
                        if message.sender.id in final_blocked_users_list or message.receiver in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
                else:
                    if message.messages.last():
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.sender.id in final_blocked_users_list or message.receiver.id in final_blocked_users_list:
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            sent_massage.append(
                                {'id': message.id, 'sender': message.sender.id, 'sender_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.receiver.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.receiver_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
            except Exception as e:
                print(e)
                pass
        for message in receiver_chat:
            try:
                if RegisterUser.objects.get(id=message.sender_id).pic_1 and RegisterUser.objects.get(
                        id=message.receiver_id).pic_1:
                    if message.messages.last():
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,
                                 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': '', 'is_image': '', 'cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
                elif RegisterUser.objects.get(id=message.sender_id).pic_1:
                    if message.messages.last():
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': RegisterUser.objects.get(id=message.sender_id).pic_1.url,
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
                elif RegisterUser.objects.get(id=message.receiver_id).pic_1:
                    if message.messages.last():
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': RegisterUser.objects.get(id=message.receiver_id).pic_1.url,
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
                else:
                    if message.messages.last():
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': message.messages.last().message,
                                 'is_image': message.messages.last().is_image,'cleared_by': message.messages.last().cleared_by,
                                 'created_at': str(message.messages.last().created_at), 'blocked': False,
                                 'message_count': len(un_read_messages)})
                    else:
                        if message.receiver.id in final_blocked_users_list or message.sender.id in final_blocked_users_list:
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': True})
                        else:
                            un_read_messages = []
                            all_messages = message.messages.all()
                            for m in all_messages:
                                if not m.read:
                                    un_read_messages.append(m)
                                else:
                                    pass
                            received_message.append(
                                {'id': message.id, 'sender': message.receiver.id,
                                 'sender_name': RegisterUser.objects.get(
                                     id=message.receiver_id).first_name,
                                 'sender_profile_pic': '',
                                 'receiver': message.sender.id, 'receiver_name': RegisterUser.objects.get(
                                    id=message.sender_id).first_name,
                                 'receiver_profile_pic': '',
                                 'last_message': '', 'is_image': '','cleared_by': message.messages.last().cleared_by,
                                 'created_at': '', 'blocked': False, 'message_count': len(un_read_messages)})
            except Exception as e:
                print('Exception', e)
                pass
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


class UnReadMessageCount(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, *args, **kwargs):
        message_count = Message.objects.filter(read=False).count()
        return Response({'count': message_count, 'status': HTTP_200_OK})


class DeleteChatRoom(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        room_id = self.request.POST['room_id']
        print(room_id)
        try:
            room_obj = ChatRoom.objects.get(id=room_id)
            sender = room_obj.sender
            receiver = room_obj.receiver
            # print(r_user,sender,receiver)
            # print(room_obj.sender is r_user)
            # print(room_obj.receiver is r_user)
            # print(room_obj.sender is r_user and room_obj.receiver is r_user)
            # print(room_obj.receiver)
            # print(room_obj.sender)
            if room_obj.sender == None and room_obj.receiver == None:
                print('inside if')
                room_obj.delete()
            else:
                print('inside else')
                if room_obj.sender == r_user:
                    room_obj.sender = None
                    room_obj.save()
                if room_obj.receiver == r_user:
                    room_obj.receiver = None
                    room_obj.save()
            return Response({'message': 'Chat room deleted successfully', 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class DeleteChatMessages(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        r_user = RegisterUser.objects.get(email=user.email)
        print(r_user.id)
        room_id = self.request.POST['room_id']
        # cleared_by = self.request.POST['cleared_by']
        print(room_id)
        try:
            room_obj = ChatRoom.objects.get(id=room_id)
            sender = room_obj.sender
            receiver = room_obj.receiver
            print(sender, receiver, r_user)
            messages = room_obj.messages.all()
            print('All Messages---', messages)
            for message in messages:
                print('Message id', message.id)
                print('inside if')
                # if message.sender == None and message.receiver == None:
                #     message.delete()
                # else:
                #     print('inside else')
                # if message.sender == r_user:
                #     print('inside nested if')
                # message.sender = None
                if message.cleared_by == '':
                    message.cleared_by = r_user.id
                    message.save()
                elif message.cleared_by:
                    message.delete()
                    # if message.receiver == r_user:
                    #     print('inside nested else')
                    #     message.receiver = None
                    #     message.save()
            return Response({"message": "Messages deleted successfully", 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})


class DeleteMessage(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        message_id = self.request.POST['message_id']
        try:
            message_obj = Message.objects.get(id=message_id)
            message_obj.delete()
            return Response({'message': 'Message deleted successfully', 'status': HTTP_200_OK})
        except Exception as e:
            return Response({'message': str(e), 'status': HTTP_400_BAD_REQUEST})
