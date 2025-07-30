from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from webhook.models import User

# Avval unregister qiling
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Keyin qayta register qiling
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'telegram_id', 'full_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'telegram_id', 'full_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'telegram_id', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )