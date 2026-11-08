from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """One login table for students, teachers and administrators."""

    STUDENT, TEACHER, ADMIN = "student", "teacher", "admin"
    ROLES = [(STUDENT, "Student"), (TEACHER, "Teacher"), (ADMIN, "Administrator")]

    role = models.CharField(max_length=10, choices=ROLES, default=STUDENT)
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_school_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_staff_member(self):
        return self.is_school_admin or self.role == self.TEACHER

    @property
    def can_manage_results(self):
        """Administrators, plus teachers the admin has marked as result admins."""
        if self.is_school_admin:
            return True
        profile = getattr(self, "teacher", None)
        return bool(self.role == self.TEACHER and profile and profile.can_upload_results)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role == self.STUDENT:
            self.role = self.ADMIN
        super().save(*args, **kwargs)


class StudentProfile(models.Model):
    GENDERS = [("F", "Female"), ("M", "Male")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student")
    reg_number = models.CharField("Registration number", max_length=20, unique=True, editable=False, blank=True)
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.PROTECT, related_name="students")
    gender = models.CharField(max_length=1, choices=GENDERS)
    date_of_birth = models.DateField(null=True, blank=True)
    guardian_name = models.CharField(max_length=120)
    guardian_phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255, blank=True)
    passport = models.ImageField(upload_to="passports/", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["school_class__order", "user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.full_name} ({self.reg_number})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @classmethod
    def next_reg_number(cls):
        from django.utils import timezone
        prefix = f"{settings.SCHOOL['reg_prefix']}-{timezone.now().year}-"
        n = cls.objects.filter(reg_number__startswith=prefix).count() + 1
        while cls.objects.filter(reg_number=f"{prefix}{n:04d}").exists():
            n += 1
        return f"{prefix}{n:04d}"

    def save(self, *args, **kwargs):
        if not self.reg_number:
            self.reg_number = self.next_reg_number()
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher")
    staff_id = models.CharField(max_length=20, blank=True)
    can_upload_results = models.BooleanField(
        "Result admin", default=False,
        help_text="Tick to let this teacher upload and publish results for every class.",
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username
