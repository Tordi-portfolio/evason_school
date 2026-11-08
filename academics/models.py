from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

# (minimum total, grade, remark)
GRADE_SCALE = [
    (70, "A", "Excellent"),
    (60, "B", "Very good"),
    (50, "C", "Good"),
    (45, "D", "Fair"),
    (40, "E", "Pass"),
    (0, "F", "Fail"),
]


def grade_for(score):
    for minimum, grade, remark in GRADE_SCALE:
        if score >= minimum:
            return grade, remark
    return "F", "Fail"


class SchoolClass(models.Model):
    name = models.CharField(max_length=10, unique=True)
    order = models.PositiveSmallIntegerField(unique=True)
    subjects = models.ManyToManyField("Subject", through="ClassSubject", related_name="classes", blank=True)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "classes"

    def __str__(self):
        return self.name

    @property
    def section(self):
        return "Junior secondary" if self.name.startswith("JSS") else "Senior secondary"


class Subject(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassSubject(models.Model):
    """Which subjects are offered in which class. Managed by the administrator."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("school_class", "subject")
        ordering = ["school_class__order", "subject__name"]

    def __str__(self):
        return f"{self.school_class}: {self.subject}"


class Term(models.Model):
    TERMS = [(1, "First term"), (2, "Second term"), (3, "Third term")]
    session = models.CharField(max_length=9, help_text="For example 2026/2027")
    term = models.PositiveSmallIntegerField(choices=TERMS)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-session", "-term"]
        unique_together = ("session", "term")

    def __str__(self):
        return f"{self.get_term_display()}, {self.session}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_current:
            Term.objects.exclude(pk=self.pk).update(is_current=False)


class Result(models.Model):
    MAX_FIRST, MAX_SECOND, MAX_EXAM = 20, 20, 60

    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    first_test = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(20)])
    second_test = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(20)])
    exam = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(60)])
    is_published = models.BooleanField(default=False, help_text="Students only see published results.")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "term")
        ordering = ["subject__name"]

    def __str__(self):
        return f"{self.student.reg_number} {self.subject} {self.term}: {self.total}"

    @property
    def total(self):
        return self.first_test + self.second_test + self.exam

    @property
    def grade(self):
        return grade_for(self.total)[0]

    @property
    def remark(self):
        return grade_for(self.total)[1]
