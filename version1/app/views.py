from django.shortcuts import render, redirect
from django.conf import settings

from app.service.forms import LoginForm
from rbac import models
from rbac.service.init_permission import init_permission
from rbac.service.basepage import BaseBookPermission


def login(request):
    """ 完整用户登陆验证及权限初始化
        参数: request, 当前用户请求对象
        返回值: 响应对象，由render或者redirect实现
    """
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if not form.is_valid():                                      # 表单验证失败
            return render(request, 'login.html', {"form": form})
        else:                                                        # 表单验证成功
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_queryset = models.User.objects.filter(username=username, password=password)

            if not user_queryset:                                    # 用户在数据库中不存在
                form.add_error(field='password', error='用户名或密码错误')
                return render(request, 'login.html', {'form': form})
            else:                                                    # 用户在数据库中存在
                init_permission(user_queryset[0], request)
                return redirect(to='/home/')

    elif request.method == 'GET':                                    # 使用elif是考虑到请求的其他方法
        form = LoginForm()
        return render(request, 'login.html', {"form": form})


def home(request):
    """ 返回用户主页面，包含用户权限
        参数: request, 用户当前请求对象
        返回值: 响应对象，将home.html渲染完成后作为响应体内容返回
    """
    feature_list = request.session[settings.FEATURE_LIST]
    page_permission = BaseBookPermission(feature_list)
    return render(request, 'home.html', {'page_permission': page_permission})

