from django import forms
from .models import SchoolClass, Subject, Term


class PickClassTermForm(forms.Form):
    school_class = forms.ModelChoiceField(SchoolClass.objects.all(), label="Class")
    term = forms.ModelChoiceField(Term.objects.all(), label="Term")


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name"]
        labels = {"name": "New subject name"}
