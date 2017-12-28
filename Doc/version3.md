# RBAC Version2.0

## 介绍与分析
- 版本2.0中，通过修改模型实现了菜单功能，但是我们在切换网页的时候会发现，当点击页面上其他权限对应超链接比如`/editbook/1/`进入到对应的页面时，菜单是完全闭合的，即"active = False"的状态，这是因为当前页面所在的url为`/editbook/1/`，在版本2.0中，其对应的`is_menu=False`并且对应超链接不存在于菜单栏中。如果遇到了有强迫症的产品经理，你现在就会多一个需求，要让你打开的页面中，新打开页面url所在的菜单在页面初始化加载完毕时是打开状态并且还要保证超链接也是`active=True`的状态。
- 于是你灵机一动：
	- 如果保证版本2模型不变的情况下，通过当前页面的url去找到url所在的权限组，再通过权限组找到对应的菜单，找到这个菜单我们就可以给其渲染功能了呀！
	- 这样做思路是对的，可是这种做法只限于一个菜单下只有一个权限组存在时才适用。我们要写的rabc既然是插件，那么就要保证普适性，因此我们要**既要保证一个菜单下可以有多个组，又要保证能通过url一层一层地找到这个菜单**
- 于是乎，我们又要对模型进行更进一步地改造
	- 我们可以将每一个权限组内的url进行更细致的划分，比如现在“图书组”中有四个权限"/listBooks/", "/addBook/", "/editBook/(\d+)/", 以及"/delBook/(\d+)/"，我们可以让除了"/listBooks/"以外的其他三个权限与"/listBooks/"建立多对一的外键关联关系，即在权限组内创建一个更小的`组内菜单`，这样当我们进入"/editBook/1/"页面的时候，只需要通过"/editBook/1/"找到其关联的"/listBooks/"，再通过"/listBooks/"确定该组所在的组以及组所在的菜单就行了。
	- 这种方式和上面方式的主要思路都是相同的，但是这种方式可以满足一个菜单下有多个组的情况



#### 表结构与字段分析
- 与版本2相比，这次我们需要对Permission表进行修改
	- 需要撤销掉`is_menu`字段，因为使用了组内菜单之后，通过组内菜单就可以实现与`is_menu`相同的功能
	- 增加一个`group_menu`字段，外键关联`Permission`表自身，并且关联字段为`Permission`表`id`。

## 设计
- 其他表结构不变，这里只给出perission表结构

```
id			url			feature			group_id		group_menu
1		/books/			showbooks	 		1				null
2		/addbook/   	addbook				1				1
3		/delbook/(\d+)/	delbook				1				1
4		/orders/		showbooks	 		1				null
5		/addorder/   	addbook				1				4
6		/delorder/(\d+)/delbook				1				4
...

```

## 项目目录结构

## 撸代码
#### 注意
- 在这之前，要保证settings.py中配置以做好，比如注册app，静态文件配置，数据库配置等

#### 1 models.py

```python
# version3/rbac/models.py

from django.db import models


class User(models.Model):
    """用户表
    普通字段:
        id, username, password
    关联字段:
        roles(多对多)
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='登录密码')

    roles = models.ManyToManyField(to='Role', verbose_name='用户拥有的角色')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户表'


class Role(models.Model):
    """角色表
    普通字段:
        id, title
    关联字段:
        permissions(多对多)
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32, verbose_name='角色名')

    permissions = models.ManyToManyField(to='Permission', verbose_name='角色拥有的权限')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '角色表'


class Permission(models.Model):
    """权限表
    普通字段:
        id, url, feature
    关联字段:
        group(多对一), group_menu(自关联: 多对一)
    """

    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=64, verbose_name='权限url路径')
    feature = models.CharField(max_length=16, verbose_name='权限对应功能')

    group_menu = models.ForeignKey(to='Permission', to_field='id', verbose_name='组内菜单', null=True, blank=True)
    group = models.ForeignKey(to='Group', to_field='id', verbose_name='所属权限组')

    def __str__(self):
        return self.feature

    class Meta:
        verbose_name_plural = '权限表'


class Group(models.Model):
    """权限组表
    普通字段:
        id, title
    关联字段:
        menu(多对一)
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16, verbose_name='权限组名')

    menu = models.ForeignKey(to='Menu', to_field='id', verbose_name='所属菜单')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '权限组表'


class Menu(models.Model):
    """菜单表
    普通字段: id, title
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '菜单表'

```

- 对应`admin.py`

```python
from django.contrib import admin
from rbac import models


admin.site.register(models.Menu)
admin.site.register(models.User)
admin.site.register(models.Permission)
admin.site.register(models.Group)
admin.site.register(models.Role)

```

- 上述操作完成后，就可以向数据库中插入数据了，再此之前需要创建一个super user登陆Django admin

#### 2 登陆验证及初始化数据
###### 2.1 设置白名单

```python
# version3/version3/settings.py


# 白名单
VALID_URLS = [
    '^/login/$',
    '^/admin.*/$',
]
```

###### 2.2 中间件part1 —— 白名单验证部分
- 先实现登陆验证中间件的白名单验证（后续会一步步补充），
	- rbac应用文件夹下创建包"middlewares"，其中创建文件`loginmd.py`
	- 代码如下

```python
# version3/rbac/

class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response
    

class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """ 完成用户登陆时白名单验证、session验证、权限验证
        Args: 
            request, 本次请求对象
        Return:
            None, 进入下一中间件或视图函数
            response, 响应，从当前中间件位置逐层向前返回响应给客户端
        """
        
        from django.conf import settings
        from re import match
        
        # 白名单验证
        current_url = request.path_info
        for regex_url in settings.VALID_URLS:
            if match(pattern=regex_url, string=current_url):
                return None
```

###### 2.3 创建登陆页面
- 登陆页面很简单，就是一个form组件，rbac作为一个权限管理组件，我们不需要为其设计多么绚丽的页面，只要实现功能即可，页面是其他项目中应用要做的事情
	- 这里仍然使用Django提供的form组件来实现form表单的渲染及验证处理，并且"forms.py"文件仍然写在app应用下，而非rbac下

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<h1>登陆</h1>

<form action="/login/" method="post" novalidate>
    {% csrf_token %}
    <p>{{ form.username }} {{ form.errors.username.0 }}</p>
    <p>{{ form.password }} {{ form.errors.password.0 }}</p>
    <input type="submit" value="登陆">
</form>

</body>
</html>
```


```python
# /version3/app/service/forms.py

from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.core.validators import RegexValidator


class LoginForm(Form):
    """ 用于登陆页面使用的Form组件类

    """
    username = fields.CharField(required=True,
                                error_messages={'required': '用户名不能为空'},
                                widget=widgets.TextInput(attrs={'placeholder': 'username'}))

    password = fields.CharField(required=True,
                                error_messages={'required': '密码不能为空'},
                                widget=widgets.TextInput(attrs={'placeholder': 'password'}),
                                validators=[RegexValidator(regex=r'\w+',
                                                           message='密码只能是数字字母下划线的组合'), ])

```


###### 2.4 初始化数据
- 完成以上之后我们就开始设计要存放在用户session中的数据了
- 对于权限方面的数据，我们仍然和版本2相同，结构如下

```
{
	'features': ['listBooks', 'home'], 
	'urls': ['/listBooks/', '/home/']
}
```

- 对于用来生成菜单的数据，我们将其结构设计成这样，这只是存放在session的结构，当我们渲染页面的时候还需要继续对其进行重构，后面会讲到

```python
[
	{'id': 1, 'url': '/listBooks/', 'feature': 'listBooks', 'group_menu': None, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 2, 'url': '/addBook/', 'feature': 'addBook', 'group_menu': 1, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 3, 'url': '/editBook/(\\d+)/', 'feature': 'editBook', 'group_menu': 1, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 4, 'url': '/delBook/(\\d+)/', 'feature': 'delBook', 'group_menu': 1, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 5, 'url': '/listOrders/', 'feature': 'listOrders', 'group_menu': None, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 6, 'url': '/addOrder/', 'feature': 'addOrder', 'group_menu': 5, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 7, 'url': '/delOrder/(\\d+)/', 'feature': 'delOrder', 'group_menu': 5, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 8, 'url': '/editOrder/(\\d+)/', 'feature': 'editOrder', 'group_menu': 5, 'menu_id': 1, 'menu_title': '管理菜单'}
	{'id': 9, 'url': '/home/', 'feature': 'home', 'group_menu': None, 'menu_id': 2, 'menu_title': '导航菜单'}
]
```

- 代码如下

```python
from django.conf import settings

from rbac import models


def init_permission(user, request):
    """ 初始化用户权限数据包括权限数据和与权限相关的菜单数据
    Args:
        user: 当前登陆并验证成功的用户
        request: 当前请求对象
    Return:
        None
    """

    permissions = user.roles.values("permissions__url",
                                    "permissions__feature",
                                    "permissions__id",
                                    "permissions__group_menu",
                                    "permissions__group__menu__id",
                                    "permissions__group__menu__title")

    # 权限相关
    permission_dict = {"features": [], "urls": []}
    for item in permissions:
        permission_dict["features"].append(item["permissions__feature"])
        permission_dict["urls"].append(item["permissions__url"])
    request.session[settings.PERMISSION_DICT] = permission_dict

    # 菜单相关
    menu_list = []
    for item in permissions:
        temp = {}
        temp["id"] = item["permissions__id"]
        temp["url"] = item["permissions__url"]
        temp["feature"] = item["permissions__feature"]
        temp["group_menu"] = item["permissions__group_menu"]
        temp["menu_id"] = item["permissions__group__menu__id"]
        temp["menu_title"] = item["permissions__group__menu__title"]
        menu_list.append(temp)
    request.session[settings.MENU_LIST] = menu_list
```

###### 2.5 完成视图函数login及相关配置
- login函数我放在了app应用而不是rbac下，在login中我将rbac的初始化权限`init_permission`函数嵌入到了登陆函数中，因为每一个项目的业务逻辑是不同的，login视图函数也一样，但是要初始化的数据结构却是相似的。
- login视图函数代码如下

```python
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
                return redirect('/home/')							# /home/ 路径需要在后面才会创建对应的home.html，这里可以代替为HttpResponse("home")
			else：
				return redirect('/login/')
        else:
            return render(request, 'login.html', {"form": form})
```


- 配置`urls.py`

```python
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
]
```


###### 2.6 完善中间件——补充session验证以及权限验证


```
class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """ 完成用户登陆时白名单验证、session验证、权限验证
        Args:
            request, 本次请求对象
        Return:
            None, 进入下一中间件或视图函数
            response, 响应，从当前中间件位置逐层向前返回响应给客户端
        """

        from django.shortcuts import redirect, HttpResponse
        from django.conf import settings
        from re import match

        # 白名单验证
        current_url = request.path_info
        for regex_url in settings.VALID_URLS:
            if match(pattern=regex_url, string=current_url):
                return None

        # session验证
        permission_dict = request.session.get(settings.PERMISSION_DICT)
        if not permission_dict:
            return redirect('/login/')

        # 权限验证
        flag = False
        for url in permission_dict:
            regex = f'^{url}$'
            if match(pattern=regex, string=current_url):
                flag = True

        if not flag:
            return HttpResponse("你没有权限访问该操作")
```

###### 2.7 生成menu html
- 现在我们要使用Django提供的inclusion tag来生成页面的html标签及数据，主要分为两个步骤
	1. 在inclusion中处理权限数据，创建一个合适的可以方便我们实现功能的数据结构，并返回该数据结构
	2. 利用处理好的数据渲染menu.html

-  一. 设计数据结构。要实现<<介绍>>中提出的需求，我们需要对当前页面url所在的menu进行标识，我们仍然使用"active"布尔值

```python
{
    1: {'menu_id': 1, 
        'menu_title': '菜单管理', 
        'active': True, 
        'children': [
                        {'feature': 'listBooks', 'url': '/listBooks/', 'active': True}
                    }, 
    2: {'menu_id': 2, 
        'menu_title': '菜单2', 
        'active': False, 
        'children': [
                        {'feature': 'listOrders', 'url': '/listOrders/', 'active': False}
                    ]}}

```

- 在rbac应用文件夹下创建包"templatetags"，并在该包下创建文件"mytag"，代码如下


```python
from django.template import Library
from django.conf import settings
from re import match

register = Library()


@register.inclusion_tag(filename='menu.html')
def menu_html(request):
    """ 生成渲染菜单的数据结构并返回该数据
    Args:
        request: 请求对象
    """

    current_url = request.path_info
    menu_list = request.session.get(settings.MENU_LIST)

    menu_dict = {}
    for item in menu_list:
        if not item['group_menu']:
            menu_dict[item['id']] = item

    for item in menu_list:
        regex_url = f'^{item["url"]}$'
        if match(pattern=regex_url, string=current_url):
            group_menu = item['group_menu']
            if group_menu:              # 当前url关联了一个组内菜单
                menu_dict[group_menu]['active'] = True
            else:                       # 当前url是组内菜单中被关联的对象(null=True)
                menu_dict[item['id']]['active'] = True

    result = {}
    for item in menu_dict.values():
        active = item.get('active')
        menu_id = item['menu_id']
        if menu_id in result:
            result[menu_id]['children'].append({'feature': item['feature'], 'url': item['url'], 'active': active})
            if active:
                result[menu_id]['active'] = True
        else:
            result[menu_id] = {
                'menu_id': item['menu_id'],
                'menu_title': item['menu_title'],
                'active': active,
                'children': [
                    {'feature': item['feature'], 'url': item['url'], 'active': active}
                ]
            }

    return {"menu_dict": result}

```


- 最后一步，按照生成的result来设计我们的模板

```python
{% for k,item in menu_dict.items %}
    <div class="item">
        <div class="item-title">{{ item.menu_title }}</div>
        {% if item.active %}
            <div class="item-permission">
        {% else %}
            <div class="item-permission hides">
        {% endif %}
            {% for v in item.children %}
                {% if v.active %}
                    <div><a href="{{ v.url }}" class="active">{{ v.feature }}</a></div>
                {% else %}
                    <div><a href="{{ v.url }}">{{ v.feature }}</a></div>
                {% endif %}
            {% endfor %}
        </div>
    </div>
    </div>
{% endfor %}

```