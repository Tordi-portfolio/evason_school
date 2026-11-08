from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("academics/", views.academics, name="academics"),
    path("admissions/", views.admissions, name="admissions"),
    path("campus-life/", views.campus_life, name="campus_life"),
    path("contact/", views.contact, name="contact"),
]
