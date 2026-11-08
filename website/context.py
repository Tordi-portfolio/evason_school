from django.conf import settings
from django.utils import timezone


def school(request):
    return {"SCHOOL": settings.SCHOOL, "year": timezone.now().year}
