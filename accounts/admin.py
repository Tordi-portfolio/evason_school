from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentProfile, TeacherProfile, User


@admin.register(User)
class SchoolUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (("School", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("School", {"fields": ("role", "first_name", "last_name", "phone")}),)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("reg_number", "full_name", "school_class", "gender", "guardian_phone")
    list_filter = ("school_class", "gender")
    search_fields = ("reg_number", "user__first_name", "user__last_name", "guardian_name")
    autocomplete_fields = ("user",)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "staff_id", "can_upload_results")
    list_filter = ("can_upload_results",)
    search_fields = ("user__username", "user__first_name", "user__last_name")
