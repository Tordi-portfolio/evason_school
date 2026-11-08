from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import StudentProfile
from .forms import SubjectForm
from .models import ClassSubject, Result, SchoolClass, Subject, Term, grade_for
from .utils import broadsheet as build_broadsheet


def _guard(check):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not check(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


staff_required = _guard(lambda u: u.is_staff_member)
results_manager_required = _guard(lambda u: u.can_manage_results)
admin_required = _guard(lambda u: u.is_school_admin)


def _current_term(request):
    wanted = request.GET.get("term") or request.POST.get("term")
    if wanted:
        term = Term.objects.filter(pk=wanted).first()
        if term:
            return term
    return Term.objects.filter(is_current=True).first() or Term.objects.first()


@staff_required
def staff_dashboard(request):
    classes = SchoolClass.objects.annotate(n_students=Count("students", distinct=True), n_subjects=Count("classsubject", distinct=True))
    context = {
        "classes": classes,
        "terms": Term.objects.all(),
        "term": _current_term(request),
        "n_students": StudentProfile.objects.count(),
        "n_subjects": Subject.objects.count(),
        "n_results": Result.objects.count(),
        "n_unpublished": Result.objects.filter(is_published=False).count(),
    }
    return render(request, "portal/staff_dashboard.html", context)


@staff_required
def students(request):
    qs = StudentProfile.objects.select_related("user", "school_class")
    class_id, q = request.GET.get("class", ""), request.GET.get("q", "").strip()
    if class_id:
        qs = qs.filter(school_class_id=class_id)
    if q:
        qs = qs.filter(Q(reg_number__icontains=q) | Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
    return render(request, "portal/students.html", {"students": qs, "classes": SchoolClass.objects.all(),
                                                    "class_id": class_id, "q": q, "term": _current_term(request)})


@staff_required
def class_students(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    term = _current_term(request)
    n_subjects = school_class.subjects.count()
    q = request.GET.get("q", "").strip()
    qs = StudentProfile.objects.filter(school_class=school_class).select_related("user")
    if q:
        qs = qs.filter(Q(reg_number__icontains=q) | Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
    entered = {r["student"]: r for r in Result.objects.filter(term=term, student__school_class=school_class)
               .values("student").annotate(n=Count("id"), pub=Count("id", filter=Q(is_published=True)))} if term else {}
    rows = [{"student": s, "entered": entered.get(s.id, {}).get("n", 0), "published": entered.get(s.id, {}).get("pub", 0)} for s in qs]
    return render(request, "portal/class_students.html", {
        "school_class": school_class, "term": term, "terms": Term.objects.all(), "rows": rows,
        "n_subjects": n_subjects, "q": q})


@results_manager_required
@require_POST
def find_student(request):
    reg = request.POST.get("reg_number", "").strip().upper()
    term = _current_term(request)
    student = StudentProfile.objects.filter(reg_number=reg).first()
    if not student:
        messages.error(request, f"No student has the registration number {reg or '(empty)'}. Check it and try again.")
        return redirect("staff_dashboard")
    if not term:
        messages.error(request, "Create a term in the admin area before uploading results.")
        return redirect("staff_dashboard")
    return redirect("enter_results", student_id=student.pk, term_id=term.pk)


@results_manager_required
def enter_results(request, student_id, term_id):
    student = get_object_or_404(StudentProfile.objects.select_related("user", "school_class"), pk=student_id)
    term = get_object_or_404(Term, pk=term_id)
    subjects = list(student.school_class.subjects.order_by("name"))
    existing = {r.subject_id: r for r in Result.objects.filter(student=student, term=term)}
    limits = (("ft", "first_test", Result.MAX_FIRST), ("st", "second_test", Result.MAX_SECOND), ("ex", "exam", Result.MAX_EXAM))
    rows, errors, to_save = [], [], []

    for s in subjects:
        old = existing.get(s.id)
        raw = {k: (request.POST.get(f"{k}_{s.id}", "").strip() if request.method == "POST"
                   else (str(getattr(old, f, "")) if old else "")) for k, f, _ in limits}
        row = {"subject": s, **raw, "total": "", "grade": ""}
        if any(raw.values()):
            nums = {}
            for k, f, mx in limits:
                try:
                    v = int(raw[k] or 0)
                    if not 0 <= v <= mx:
                        raise ValueError
                    nums[f] = v
                except ValueError:
                    errors.append(f"{s.name}: {f.replace('_', ' ')} must be a whole number from 0 to {mx}.")
            if len(nums) == 3:
                row["total"] = sum(nums.values())
                row["grade"] = grade_for(row["total"])[0]
                to_save.append((s, nums))
        rows.append(row)

    publish = request.POST.get("publish") == "on" if request.method == "POST" else (all(r.is_published for r in existing.values()) and bool(existing))
    if request.method == "POST":
        if errors:
            for e in errors:
                messages.error(request, e)
        elif not subjects:
            messages.error(request, "This class has no subjects yet. Ask the administrator to assign subjects first.")
        else:
            for s, nums in to_save:
                Result.objects.update_or_create(student=student, subject=s, term=term,
                                                defaults={**nums, "is_published": publish, "updated_by": request.user})
            state = "published to the student's dashboard" if publish else "saved as a draft (the student cannot see it yet)"
            messages.success(request, f"{student.full_name}: {len(to_save)} subject result(s) {state}.")
            return redirect(f"{redirect('class_students', class_id=student.school_class_id).url}?term={term.pk}")

    return render(request, "portal/enter_results.html", {"student": student, "term": term, "rows": rows,
                                                         "publish": publish, "no_subjects": not subjects})


@staff_required
def broadsheet(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    term = _current_term(request)
    rows = build_broadsheet(school_class, term) if term else []
    return render(request, "portal/broadsheet.html", {"school_class": school_class, "term": term, "terms": Term.objects.all(), "rows": rows})


@results_manager_required
@require_POST
def publish(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    term = get_object_or_404(Term, pk=request.POST.get("term"))
    state = request.POST.get("action") == "publish"
    n = Result.objects.filter(student__school_class=school_class, term=term).update(is_published=state)
    messages.success(request, f"{n} result(s) for {school_class} {'published' if state else 'moved back to draft'}.")
    return redirect(f"{redirect('class_students', class_id=school_class.pk).url}?term={term.pk}")


@admin_required
def subjects(request):
    form = SubjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        subject = form.save()
        messages.success(request, f"{subject.name} added. Now tick the classes that offer it.")
        return redirect("subjects")
    classes = SchoolClass.objects.prefetch_related("subjects")
    return render(request, "portal/subjects.html", {"classes": classes, "form": form, "all_subjects": Subject.objects.all()})


@admin_required
def class_subjects(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    if request.method == "POST":
        chosen = set(map(int, request.POST.getlist("subjects")))
        current = set(ClassSubject.objects.filter(school_class=school_class).values_list("subject_id", flat=True))
        ClassSubject.objects.filter(school_class=school_class, subject_id__in=current - chosen).delete()
        ClassSubject.objects.bulk_create([ClassSubject(school_class=school_class, subject_id=i) for i in chosen - current])
        messages.success(request, f"{school_class} now offers {len(chosen)} subject(s).")
        return redirect("subjects")
    selected = set(ClassSubject.objects.filter(school_class=school_class).values_list("subject_id", flat=True))
    return render(request, "portal/class_subjects.html", {"school_class": school_class, "subjects": Subject.objects.all(), "selected": selected})
