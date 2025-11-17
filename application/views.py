
from django.contrib.auth import authenticate, login

from django.shortcuts import render, redirect
from .models import User,UserProfile
from application.forms import SignUpForm, UserProfileForm
from django.contrib import messages
# Create your views here.
def index(request):
    return render(request, 'index.html')

def register(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user=authenticate(request, username=username,password=raw_password)
            login(request, user)
            return redirect('login.html')
        else:
            messages.error(request, 'Please correct the error below.')

    return render(request, 'register.html',{'form':form})

def login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect(' ')
    return render(request, 'login.html')

