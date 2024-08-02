from django.contrib import admin
from .models import User


@admin.register(User)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')