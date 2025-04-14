from django.shortcuts import render
from accounts.decorators import login_and_verified_required

# Create your views here.
@login_and_verified_required
def index_view(request):
    return render(request, "main/index.html")

def landing_view(request):
    return render(request, "main/landing.html")