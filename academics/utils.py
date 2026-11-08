from django.db.models import Count, F, Sum

from .models import Result, grade_for

TOTAL = Sum(F("first_test") + F("second_test") + F("exam"))


def term_summary(student, term, published_only=True):
    """Everything a result sheet needs: rows, total, average, grade and class position."""
    qs = Result.objects.filter(student=student, term=term).select_related("subject")
    if published_only:
        qs = qs.filter(is_published=True)
    results = list(qs.order_by("subject__name"))
    total = sum(r.total for r in results)
    count = len(results)
    average = round(total / count, 1) if count else 0

    position = class_size = None
    if count:
        ranked = Result.objects.filter(term=term, student__school_class=student.school_class)
        if published_only:
            ranked = ranked.filter(is_published=True)
        totals = [row["t"] for row in ranked.values("student").annotate(t=TOTAL)]
        position = 1 + sum(1 for t in totals if t > total)
        class_size = len(totals)

    grade, remark = grade_for(average)
    return {"results": results, "total": total, "count": count, "max_total": count * 100,
            "average": average, "grade": grade, "remark": remark,
            "position": position, "class_size": class_size}


def broadsheet(school_class, term):
    """One row per student in the class, ranked by total score."""
    from accounts.models import StudentProfile
    agg = {row["student"]: row for row in
           Result.objects.filter(term=term, student__school_class=school_class)
           .values("student").annotate(t=TOTAL, n=Count("id"))}
    rows = []
    for s in StudentProfile.objects.filter(school_class=school_class).select_related("user"):
        a = agg.get(s.id)
        total, n = (a["t"], a["n"]) if a else (0, 0)
        avg = round(total / n, 1) if n else 0
        rows.append({"student": s, "total": total, "count": n, "average": avg, "grade": grade_for(avg)[0] if n else "-"})
    scored = sorted((r for r in rows if r["count"]), key=lambda r: -r["total"])
    for r in rows:
        r["position"] = (1 + sum(1 for o in scored if o["total"] > r["total"])) if r["count"] else None
    rows.sort(key=lambda r: (r["position"] is None, r["position"] or 0, r["student"].full_name))
    return rows
