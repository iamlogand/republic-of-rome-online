from django.shortcuts import render


# Backend index page
def index(request):
    return render(request, "index.html")
