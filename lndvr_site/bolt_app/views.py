from django.shortcuts import render

# Create your views here.

def bolt(request):
    return render(request, "bolt.html", {'current_page':'bolt'})