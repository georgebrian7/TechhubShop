from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from application.models import UserProfile

class ProfileInline(admin.StackedInline):
    model = UserProfile

# extend user

class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInline]

# unregister old user
admin.site.unregister(User)
admin.site.register(User, UserAdmin)