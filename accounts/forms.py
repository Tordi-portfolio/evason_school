from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

from academics.models import SchoolClass
from .models import StudentProfile, User


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Registration number or username",
                               widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "EIS-2026-0001"}))

    def clean_username(self):
        value = self.cleaned_data["username"].strip()
        return value.upper() if value.upper().startswith("EIS-") else value


class StudentRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=60)
    last_name = forms.CharField(max_length=60)
    gender = forms.ChoiceField(choices=StudentProfile.GENDERS)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    school_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all(), label="Your class",
                                          empty_label="Select your class (JSS1 to SS3)")
    guardian_name = forms.CharField(max_length=120, label="Parent or guardian name")
    guardian_phone = forms.CharField(max_length=30, label="Parent or guardian phone")
    email = forms.EmailField(required=False, label="Email (optional)")
    address = forms.CharField(max_length=255, required=False, label="Home address")
    passport = forms.ImageField(required=False, label="Passport photograph")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Create a password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "The two passwords do not match.")
            else:
                try:
                    password_validation.validate_password(p1)
                except forms.ValidationError as exc:
                    self.add_error("password1", exc)
        return data

    @transaction.atomic
    def save(self):
        d = self.cleaned_data
        reg = StudentProfile.next_reg_number()
        user = User.objects.create_user(
            username=reg, password=d["password1"], first_name=d["first_name"].strip().title(),
            last_name=d["last_name"].strip().title(), email=d.get("email", ""), role=User.STUDENT,
        )
        return StudentProfile.objects.create(
            user=user, reg_number=reg, school_class=d["school_class"], gender=d["gender"],
            date_of_birth=d["date_of_birth"], guardian_name=d["guardian_name"],
            guardian_phone=d["guardian_phone"], address=d.get("address", ""), passport=d.get("passport") or "",
        )
