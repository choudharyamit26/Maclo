from .models import User, UserNotification, TermsCondition

from django.contrib import admin

admin.site.register(User)
admin.site.register(UserNotification)
admin.site.register(TermsCondition)
