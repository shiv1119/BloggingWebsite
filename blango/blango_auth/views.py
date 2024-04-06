from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from blog.models import AuthorProfile
from .forms import AuthorProfileForm
from django.contrib.auth.decorators import login_required
from blog.models import Post
from django.shortcuts import redirect



@login_required
def profile(request):
    return render(request, "blango_auth/profile.html")

def custom_logout(request):
    logout(request)
    return redirect("login")



