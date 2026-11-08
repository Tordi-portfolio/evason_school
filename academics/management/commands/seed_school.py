from django.core.management.base import BaseCommand
from django.utils import timezone

from academics.models import ClassSubject, SchoolClass, Subject, Term

JUNIOR = ["English Language", "Mathematics", "Basic Science", "Basic Technology", "Social Studies", "Civic Education",
          "Computer Studies", "Agricultural Science", "Business Studies", "Christian Religious Studies",
          "Cultural and Creative Arts", "Physical and Health Education", "Igbo Language", "Home Economics"]
SENIOR_CORE = ["English Language", "Mathematics", "Civic Education", "Computer Studies"]
SENIOR_EXTRA = ["Physics", "Chemistry", "Biology", "Further Mathematics", "Economics", "Government", "Literature in English",
                "Geography", "Financial Accounting", "Commerce", "Agricultural Science", "Christian Religious Studies"]


class Command(BaseCommand):
    help = "Create JSS1-SS3, a starter subject list and the current term."

    def handle(self, *args, **options):
        names = ["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]
        for i, name in enumerate(names, 1):
            cls, _ = SchoolClass.objects.get_or_create(name=name, defaults={"order": i})
            wanted = JUNIOR if name.startswith("JSS") else SENIOR_CORE + SENIOR_EXTRA
            for subject_name in wanted:
                subject, _ = Subject.objects.get_or_create(name=subject_name)
                ClassSubject.objects.get_or_create(school_class=cls, subject=subject)
        now = timezone.now()
        start = now.year if now.month >= 9 else now.year - 1
        Term.objects.get_or_create(session=f"{start}/{start + 1}", term=1, defaults={"is_current": True})
        self.stdout.write(self.style.SUCCESS("Classes, subjects and the current term are ready."))
