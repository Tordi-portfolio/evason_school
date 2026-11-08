from django.urls import path
from . import views

urlpatterns = [
    path("", views.staff_dashboard, name="staff_dashboard"),
    path("find/", views.find_student, name="find_student"),
    path("students/", views.students, name="students"),
    path("class/<int:class_id>/", views.class_students, name="class_students"),
    path("class/<int:class_id>/broadsheet/", views.broadsheet, name="broadsheet"),
    path("class/<int:class_id>/publish/", views.publish, name="publish"),
    path("results/<int:student_id>/<int:term_id>/", views.enter_results, name="enter_results"),
    path("subjects/", views.subjects, name="subjects"),
    path("subjects/<int:class_id>/", views.class_subjects, name="class_subjects"),
]
