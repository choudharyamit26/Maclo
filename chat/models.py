from django.contrib.auth import get_user_model
from django.db import models
from src.models import RegisterUser


class Message(models.Model):
    sender = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, related_name='message_sender')
    # sender = models.CharField(max_length=10000)
    receiver = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, related_name='message_receiver')
    # receiver = models.CharField(max_length=10000)
    message = models.CharField(default='', null=True, blank=True, max_length=2000)
    # image = models.ImageField(null=True, blank=True)
    is_image = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatRoom(models.Model):
    sender = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, related_name='chat_room_sender')
    receiver = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, related_name='chat_room_receiver')
    # sender = models.CharField(max_length=10000)
    # receiver = models.CharField(max_length=10000)
    messages = models.ManyToManyField(Message)
    # image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
#
# User = get_user_model()
#
#
# class Contact(models.Model):
#     user = models.ForeignKey(
#         RegisterUser, related_name='friends', on_delete=models.CASCADE)
#     friends = models.ManyToManyField('self', blank=True)
#
#     def __str__(self):
#         return self.user.first_name
#
#
# class Message(models.Model):
#     contact = models.ForeignKey(
#         Contact, related_name='messages', on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.contact.user.first_name
#
#
# class Chat(models.Model):
#     participants = models.ManyToManyField(
#         Contact, related_name='chats', blank=True)
#     messages = models.ManyToManyField(Message, blank=True)
#
#     def __str__(self):
#         return "{}".format(self.pk)
