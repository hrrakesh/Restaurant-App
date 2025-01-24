from django.contrib import admin
from .models import User, UserProfile, NewsSub
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    ordering = ('-date_join',)
    filter_horizontal = ()
    list_filter =('role',)
    fieldsets = ()

class NewsSubAdmin(admin.ModelAdmin):
    list_display = ('email',)
    

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
admin.site.register(NewsSub,NewsSubAdmin)