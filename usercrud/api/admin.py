from django.contrib import admin
from .models import UserDetail

@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "name", 
        "father_name", 
        "date_of_birth", 
        "email", 
        "phone_number", 
        "is_deleted", 
        "created_at"
    )
    list_filter = ("is_deleted", "created_at")
    search_fields = ("name", "father_name", "email", "phone_number")
    ordering = ("-created_at",)
