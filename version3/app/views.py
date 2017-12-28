from django.shortcuts import render, redirect

from app.service.forms import LoginForm
from rbac import models
from rbac.service.init_permission import init_permission


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
    elif request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user_queryset = models.User.objects.filter(**form.cleaned_data)
            if user_queryset:
                init_permission(user_queryset[0], request)
                return redirect('/home/')
            else:
                return redirect('/login/')
        else:
            return render(request, 'login.html', {"form": form})


def home(request):
    return render(request, 'home.html')