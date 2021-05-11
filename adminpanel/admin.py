from .models import User, UserNotification, TermsCondition,SafetyTips

from django.contrib import admin

admin.site.register(User)
admin.site.register(UserNotification)
admin.site.register(TermsCondition)
admin.site.register(SafetyTips)
