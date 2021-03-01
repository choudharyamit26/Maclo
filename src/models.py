from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
# from rest_framework.response import Response
# from rest_framework.status import HTTP_200_OK

RELATIONSHIP_STATUS = (
    ("Single", "Single"),
    ("Commited", "Commited"),
    ("Divorcee", "Divorcee"),
    ("Married", "Married"),
    ("Widow", "Widow"),
    ("Engaged", "Engaged"),
    ("Other", "Other")
)
LOCATION = (
    ("Noida", "Noida"),
    ("Delhi", "Delhi"),
    ('Mumbai', 'Mumbai'),
    ('Banglore', 'Banglore'),
    ('Gurgaon', 'Gurgaon'),
    ('Chennai', 'Chennai'),
    ('Kerala', 'Kerala'),
    ('Gujrat', 'Gujrat'),
    ('Ahmedabad', 'Ahmedabad')
)
PROFESSION = (
    ("IT Support", "IT Support"),
    ("Software Developer", "Software Developer"),
    ('Model', 'Model'),
    ('Director', 'Director'),
    ('Fitness Trainer', 'Fitness Trainer'),
    ('Doctor', 'Doctor'),
    ('Actor', 'Actor'),
    ('Nutritionist', 'Nutritionist'),
    ('Human Resource', 'Human Resource')
)
QUALIFICATION = (
    ('Matriculate', 'Matriculate'),
    ('Intermediate', 'Intermediate'),
    ("Bachelor's", "Bachelor's"),
    ("Matser's", "Matser's"),
    ("Doctrate", "Doctrate"),
)

COLLEGES = (("IIT", "IIT"),
            ("IIIT", "IIT"),
            ("NIT", "NIT"),
            ("IISC", "IISC"),
            ("BITS PILANI", "BITS PILANI"),
            ("AIIMS", "AIIMS"),
            ("IIM", "IIM")
            )
FOOD_TYPE = (("Veg", "Veg"), ("Non-Veg", "Non-Veg"))
VEHICLES = (("Car", "Car"), ("Bike", "Bike"), ("Both", "Both"))
UNIVERSITY = (
    ("DU", "DU"),
    ("JNU", "JNU"),
    ("BHU", "BHU"),
    ("CCSU", "CCSU"),
    ("IPU", "IPU"),
    ("AKTU", "AKTU"),
)

PREFRENCE_FIRST_DATE = (
    ("Tea", "Tea"),
    ("Coffee", "Coffee"),
    ("Soft Drinks", "Soft Drinks"),
    ("Beer", "Beer"),
    ("Wine", "Wine"),
    ("Whisky", "Whisky")
)

METTING_STATUS = (('Hold', 'Hold'), ('Accept', 'Accept'), ('Decline', 'Decline'))
BOOL_CHOICES = (('Yes', 'Yes'), ('No', 'No'))

GENDER = (('Male', 'Male'), ('Female', 'Female'), ('Custom', 'Custom'))

STATUS = (('Not Completed', 'Not Completed'), ('Completed', 'Completed'))


class RegisterUser(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    email = models.EmailField(default='')
    phone_number = models.CharField(default='', max_length=13)
    first_name = models.CharField(default='', max_length=100)
    last_name = models.CharField(default='', max_length=100)
    gender = models.CharField(default='', max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    job_profile = models.CharField(max_length=100, null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    qualification = models.CharField(default="", max_length=100, null=True, blank=True)
    relationship_status = models.CharField(default='', max_length=100, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    fav_quote = models.CharField(default='', max_length=1000)
    religion = models.CharField(default='', max_length=100, null=True, blank=True)
    body_type = models.CharField(default='', max_length=100)
    zodiac_sign = models.CharField(default='', max_length=100)
    taste = models.CharField(default='', max_length=100)
    created_at = models.DateField(auto_now_add=True)
    verified = models.BooleanField(default=False, max_length=10)
    fb_signup = models.CharField(default='No', choices=BOOL_CHOICES, max_length=10)
    pic_1 = models.ImageField(upload_to='media', null=True, blank=True)
    pic_2 = models.ImageField(upload_to='media', null=True, blank=True)
    pic_3 = models.ImageField(upload_to='media', null=True, blank=True)
    pic_4 = models.ImageField(upload_to='media', null=True, blank=True)
    pic_5 = models.ImageField(upload_to='media', null=True, blank=True)
    pic_6 = models.ImageField(upload_to='media', null=True, blank=True)

    # pic_7 = models.ImageField(upload_to='media', null=True, blank=True)
    # pic_8 = models.ImageField(upload_to='media', null=True, blank=True)
    # pic_9 = models.ImageField(upload_to='media', null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def get_user_age(self):
        age = timezone.now().year - self.date_of_birth.year
        return age


class SubscriptionPlans(models.Model):
    name = models.CharField(default='My subscription', max_length=500)
    description = models.TextField()
    feature_likes = models.CharField(default='Feature', max_length=200, null=True, blank=True)
    likes_number = models.IntegerField(null=True, blank=True)
    feature_superlikes = models.CharField(default='super like', max_length=100, null=True, blank=True)
    superlikes_number = models.IntegerField(null=True, blank=True)
    feature_rewind = models.CharField(default='rewind', max_length=300, null=True, blank=True)
    number_rewind = models.IntegerField(null=True, blank=True)
    ads_comes_or_not = models.CharField(default='ads', max_length=100, null=True, blank=True)
    search_filters = models.CharField(default='search_filter', max_length=100, null=True, blank=True)
    see_likes = models.CharField(default='yes', max_length=100, null=True, blank=True)
    read_recipient = models.CharField(default='yes', max_length=100, null=True, blank=True)
    feature_count = models.IntegerField()
    amount = models.IntegerField()
    validity = models.CharField(default='1 month', max_length=100)
    valid_till = models.CharField(default='2020-07-01', max_length=100, null=True, blank=True)
    active = models.CharField(default='No', choices=BOOL_CHOICES, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class UserDetail(models.Model):
    bio = models.CharField(default='', max_length=600, null=True, blank=True)
    phone_number = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, null=True, blank=True)
    discovery = models.PointField(srid=4326, geography=True, null=True, blank=True)
    distance_range = models.IntegerField(default=5, null=True, blank=True)
    min_age_range = models.IntegerField(default=18, null=True, blank=True)
    max_age_range = models.IntegerField(default=50, null=True, blank=True)
    hometown = models.CharField(default='', max_length=300, null=True, blank=True)
    living_in = models.CharField(default='', max_length=300, null=True, blank=True)
    profession = models.CharField(default="", max_length=100, null=True, blank=True)
    college_name = models.CharField(default='', max_length=100, null=True, blank=True)
    university = models.CharField(default='', max_length=200, null=True, blank=True)
    personality = models.CharField(default='', max_length=500, null=True, blank=True)
    food_type = models.CharField(default='', max_length=100, null=True, blank=True)
    owns = models.CharField(default='', max_length=200, null=True, blank=True)
    # owns = ArrayField(models.CharField(max_length=200, blank=True, null=True), default=list, blank=True, null=True)
    preference_first_date = models.CharField(default='', max_length=150, null=True, blank=True)
    fav_music = models.CharField(default='', max_length=500, null=True, blank=True)
    travelled_place = models.CharField(default='', max_length=500, null=True, blank=True)
    once_in_life = models.CharField(default='', max_length=500, null=True, blank=True)
    exercise = models.CharField(default='Yes', max_length=10, null=True, blank=True)
    looking_for = models.CharField(default="", max_length=500, null=True, blank=True)
    interest = models.CharField(default="", max_length=500, null=True, blank=True)
    fav_food = models.CharField(default='', max_length=500, null=True, blank=True)
    fav_pet = models.CharField(default='', max_length=100, null=True, blank=True)
    smoke = models.CharField(default='No', max_length=10, null=True, blank=True)
    drink = models.CharField(default='No', max_length=10, null=True, blank=True)
    subscription_purchased = models.CharField(default='No', max_length=100, null=True, blank=True)
    subscription_purchased_at = models.DateField(null=True, blank=True)
    subscription = models.ForeignKey(SubscriptionPlans, on_delete=models.CASCADE, null=True, blank=True)
    deactivated = models.BooleanField(default=False)


class UserInstagramPic(models.Model):
    phone_number = models.ForeignKey(RegisterUser, default=1, on_delete=models.CASCADE)
    # username = models.CharField(default='username', max_length=100)
    # password = models.CharField(default='password', max_length=100)
    # insta_pic_1 = models.ImageField(null=True, blank=True)
    # insta_pic_2 = models.ImageField(null=True, blank=True)
    # insta_pic_3 = models.ImageField(null=True, blank=True)
    # insta_pic_4 = models.ImageField(null=True, blank=True)
    # insta_pic_5 = models.ImageField(null=True, blank=True)
    # insta_pic_6 = models.ImageField(null=True, blank=True)
    # insta_pic_7 = models.ImageField(null=True, blank=True)
    # insta_pic_8 = models.ImageField(null=True, blank=True)
    # insta_pic_9 = models.ImageField(null=True, blank=True)
    # insta_pic_10 = models.ImageField(null=True, blank=True)
    insta_pic_1 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_2 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_3 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_4 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_5 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_6 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_7 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_8 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_9 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_pic_10 = models.CharField(default='', null=True, blank=True, max_length=5000)
    insta_connect = models.BooleanField(default=False)


class UserSettings(models.Model):
    phone_number = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(default='Delhi', choices=LOCATION, max_length=100)
    max_distance = models.IntegerField(default=10)
    age_range = models.IntegerField(default='18', validators=[MinValueValidator(18), MaxValueValidator(130)])
    show_me_on_app = models.CharField(choices=BOOL_CHOICES, max_length=100)


class MatchedUser(models.Model):
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    liked_by_me = models.ManyToManyField(RegisterUser, default=1, related_name='likedbyme')
    disliked_by_me = models.ManyToManyField(RegisterUser, default=1, related_name='dislikedbyme')
    super_liked_by_me = models.ManyToManyField(RegisterUser, default=1, related_name='superlikedbyme')
    matched = models.CharField(default='No', choices=BOOL_CHOICES, max_length=100)
    super_matched = models.CharField(default='No', choices=BOOL_CHOICES, max_length=100)
    matched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class RequestMeeting(models.Model):
    phone_number = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    status = models.CharField(default='Hold', choices=METTING_STATUS, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class ScheduleMeeting(models.Model):
    scheduled_with = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, related_name='scheduled_with')
    scheduled_by = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    venue = models.TextField()
    description = models.TextField()
    status = models.CharField(default='Not Completed', max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    phone_number = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    feedback = models.TextField()
    stars = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ContactUs(models.Model):
    phone_number = models.BigIntegerField(default='+9199999')
    email = models.EmailField(default='support@maclo.com', max_length=100)


class ContactUsQuery(models.Model):
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(default='', max_length=1000)
    description = models.TextField(default='')


class AboutUs(models.Model):
    about_us = models.TextField()


class PopNotification(models.Model):
    user1 = models.ForeignKey(RegisterUser, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    # title = models.CharField(default='Met', max_length=100)
    meeting = models.ForeignKey(ScheduleMeeting, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


class PrivacyPolicy(models.Model):
    content = models.TextField()


class DeactivateAccount(models.Model):
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    deactivated = models.BooleanField(default=False)


class BlockedUsers(models.Model):
    user = models.ForeignKey(RegisterUser, on_delete=models.CASCADE)
    blocked = models.ManyToManyField(RegisterUser, related_name='blocked')
