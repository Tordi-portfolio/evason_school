from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from academics.models import Term
from academics.utils import term_summary
from .forms import StudentRegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = StudentRegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        profile = form.save()
        login(request, profile.user)
        messages.success(request, f"Welcome to Evason, {profile.user.first_name}. Your registration number is "
                                  f"{profile.reg_number}. Write it down: you will use it to log in.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    """Send each person to the right home after login."""
    if request.user.is_staff_member:
        return redirect("staff_dashboard")
    return redirect("student_dashboard")


@login_required
def student_dashboard(request):
    profile = getattr(request.user, "student", None)
    if profile is None:
        messages.error(request, "This account has no student record. Please contact the school office.")
        return redirect("home")

    # A student can only ever read their own, published results.
    terms = list(Term.objects.filter(result__student=profile, result__is_published=True).distinct())
    selected = None
    if terms:
        wanted = request.GET.get("term")
        selected = next((t for t in terms if str(t.pk) == wanted), None) or \
                   next((t for t in terms if t.is_current), terms[0])
    summary = term_summary(profile, selected) if selected else None
    return render(request, "accounts/student_dashboard.html",
                  {"profile": profile, "terms": terms, "term": selected, "summary": summary})
