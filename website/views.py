from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import ContactForm


def home(request):
    return render(request, "website/home.html")

def about(request):
    return render(request, "website/about.html")

def academics(request):
    return render(request, "website/academics.html")

def admissions(request):
    return render(request, "website/admissions.html")

def campus_life(request):
    return render(request, "website/campus_life.html")

def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thank you. Your message has reached the school office and we will reply within two working days.")
        return redirect("contact")
    return render(request, "website/contact.html", {"form": form})
