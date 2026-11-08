from django.contrib import admin
from .models import ClassSubject, Result, SchoolClass, Subject, Term


class ClassSubjectInline(admin.TabularInline):
    model = ClassSubject
    extra = 3


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    inlines = [ClassSubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_current")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "term", "first_test", "second_test", "exam", "total", "grade", "is_published")
    list_filter = ("term", "subject", "student__school_class", "is_published")
    search_fields = ("student__reg_number", "student__user__first_name", "student__user__last_name")
