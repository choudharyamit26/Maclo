from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models

from src.models import RegisterUser
from django.urls import reverse

BOOL_CHOICES = (('Yes', 'Yes'), ('No', 'No'))


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255)
    social_type = models.CharField(max_length=255)
    social_id = models.CharField(max_length=255)
    device_token = models.CharField(default='', null=True, blank=True, max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class AdminNotification(models.Model):
    title = models.CharField(default='Admin notification', max_length=300)
    users = models.ManyToManyField(RegisterUser)
    description = models.TextField()


class Transaction(models.Model):
    payment_id = models.CharField(default='0000', max_length=100)
    order_id = models.CharField(default='0000', max_length=100)
    order_date = models.DateField()
    order_time = models.TimeField()
    total_amount = models.IntegerField()
    payment_mode = models.CharField(default='Visa', max_length=100)


class AdminNotificationSetting(models.Model):
    notification = models.CharField(default='Yes', choices=BOOL_CHOICES, max_length=100)


class UserNotification(models.Model):
    """Notification model"""
    to = models.ForeignKey(User, on_delete=models.CASCADE)
    extra_text = models.CharField(default='', max_length=100)
    title = models.CharField(default='title', max_length=200)
    # title_in_arabic = models.CharField(default='title', max_length=200)
    body = models.CharField(default='body', max_length=200)
    # body_in_arabic = models.CharField(default='body', max_length=200)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class TermsCondition(models.Model):
    content = models.TextField(default='')
