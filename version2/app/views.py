from django.shortcuts import render, redirect

from rbac.service.init_permission import init_permission
from app.service.forms import LoginForm
from rbac import models


def login(request):
    """ 完整用户登陆验证及权限初始化，返回的响应可以根据项目需要修改成Ajax对应的HttpResponse
    Args:
        request, 当前用户请求对象
    Return:
        响应对象，由render或者redirect实现
    """

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if not form.is_valid():  # 表单验证失败
            return render(request, 'login.html', {"form": form})
        else:  # 表单验证成功
            user_queryset = models.User.objects.filter(**form.cleaned_data)
            if not user_queryset:  # 用户在数据库中不存在
                form.add_error(field='password', error='用户名或密码错误')
                return render(request, 'login.html', {'form': form})
            else:  # 用户在数据库中存在
                init_permission(user_queryset[0], request)  # 初始化用户权限数据
                return redirect(to='/home/')

    elif request.method == 'GET':  # 为了增强程序的可扩展性，没有使用else
        form = LoginForm()
        return render(request, 'login.html', {"form": form})


def home(request):
    return render(request, 'home.html')


def list_books(request):
    return render(request, 'listBooks.html')


def list_orders(request):
    return render(request, 'listOrders.html')


def add_book(request):
    return render(request, 'addBook.html')


def add_order(request):
    return render(request, 'addOrder.html')
