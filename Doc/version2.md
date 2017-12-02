# RBAC Version2.0

## 介绍
- 在版本1中，仅仅实现的是将每个用户的权限内容变成a标签显示在页面中。产品经理当然无法接受这样简陋的设计，现在他要求我们要在页面上显示左侧菜单，将权限放在一个个菜单中。为了混口饭吃，所以我们要对rbac进行再次改进。于是有了这个版本2


## 分析
#### 需求分析
- 要让HTML页面上生成菜单，并且要把权限放在菜单里，那么不同的权限肯定要放在不同的菜单中，比如访问`/home/`页面的权限就不要和`/showbooks/`放在同一个菜单下。当然我们也要考虑浏览器能显示的HTML页面的高度，因此我们可以将相似的但是却是不同种类的权限放在同一个菜单下，这样就不会因为菜单数目过多而不方便浏览。比如将“订单列表”和“图书列表”放在一个菜单下
- 问题又来了，“订单列表”与“图书列表”这两种类型的权限显然也需要我们区分开，这样更**细致的划分有利于我们后面功能的实现**，比如只想在菜单中显示与订单相关的权限，那么此时我们就不能将与“图书管理”有关的权限与“订单管理”相关的权限混在一起，所以，除了使用菜单对权限进行外层的宏观划分之外，还要在每一个菜单内部对每一个类型的权限进行更细致的划分


#### 表结构分析
- 用户表与角色表和版本1中相同。在这个版本中，我们需要对权限表进行调整，并且要新增权限组表和菜单组表

- 权限与权限组之间应该是多对一的关系，比如将"图书列表"，"增加图书"，"删除图书"，"编辑图书"与"图书组关联"，将"订单列表"，"增加订单"，"删除订单"，"编辑订单"与"订单组关联"。
- 为了更方便的管理，多个权限组应该与一个菜单关联，比如我们可以将"图书组"，"订单组"放在"管理菜单"中。


#### 字段分析
- 权限组中字段除了"url", "feature"以及关联的"roles"之外，还应该增加一个专门用来判断权限是否应该显示在菜单中，因为对于有些权限比如"图书列表"、"订单列表"，他们的url是不变的（没有包含正则表达式），而对于"删除图书"，"编辑图书"等权限，其作用的对象数据库中指定的单个记录，因此应该显示在页面的内容中。我们使用`is_menu`字段来区分某一条记录中的权限是否可以在菜单中显示

- 除了`is_menu`，权限表还要建立外键`group`，与权限组表关联

- 权限组表中至少应包含`id`, `title`（权限组名），以及作为外键关联到菜单中的一条记录

- 菜单表中，需要有`id`, `title`（菜单名）来作为一条记录的属性


## 设计
#### 表结构
###### 用户表

```
id			username		pasword
1			ziawang			pass
2			jay				passjay
...
```

###### 角色表


```
id 			title
1			admin
2			reader	
...

```

###### 权限表

```
id			url			feature			is_menu		group_id
1		/books/			showbooks		 true			1
2		/addbook/   	addbook			 true			1
3		/del/(\d+)/		delbook			 false			1
4		/orders/		showorders		 true			2
5		/addorder/		addorder		 true			2

...

```

###### 权限组表

```
id 			title		menu_id
1			图书组		1
2			订单组		1
3			其他组		2

...

```

###### 菜单表

```
id			title		
1			管理菜单
2			导航菜单
...

```


###### 用户&角色表


```
id			User		Role
1			 1			 1
2			 1			 2
3			 2			 1
...

```

###### 角色&权限表


```
id			permission_id		role_id
1				1					1
2				1					2
3				2					1
....
```


#### 项目目录结构

```
version2
│
│
│  db.sqlite3
│  manage.py
│
├─app
│  │  admin.py
│  │  apps.py
│  │  models.py
│  │  tests.py
│  │  views.py
│  │  __init__.py
│  │
│  ├─migrations
│  │    __init__.py
│  │
│  ├─service
│  │    forms.py
│  │  
│  │ 
│  │       
│  │
│  ├─static
│  │  └─app
│  │         app.css
│  │         app.js
│  │
│  ├─templatetags
│       mytag.py
│          
│
├─rbac
│  │  admin.py
│  │  apps.py
│  │  models.py
│  │  tests.py
│  │  views.py
│  │  __init__.py
│  │
│  ├─middlewares
│  │    loginmd.py
│  │  
│  │
│  ├─migrations
│  │    0001_initial.py
│  │    __init__.py
│  │  
│  │
│  ├─service
│       init_permission.py
│       __init__.py
│  
│
├─templates
│      addBook.html
│      addOrder.html
│      base.html
│      home.html
│      listBooks.html
│      listOrders.html
│      login.html
│      menu.html
│
└─version2
      settings.py
      urls.py
      wsgi.py
      __init__.py


```

###### 配置项目
- 创建完项目之后，我们第一步就要完成项目必要的配置，至少应包括
	1. 注册app
	2. 数据库

- 具体操作与版本1相同

## 开始撸代码

#### 1. models.py
- 数据库是整个项目的基础，所以我们还是要从数据设计开始


```python
# version2/rbac/models.py
from django.db import models


class User(models.Model):
    """ 用户表
        普通字段: id, username, password
        关联字段: roles(多对多)
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')

    roles = models.ManyToManyField(to='Role', verbose_name='角色', blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户表'


class Role(models.Model):
    """ 角色表
        普通字段: id, title
        关联字段:
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16)

    permissions = models.ManyToManyField(to='Permission', verbose_name='权限', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '角色表'


class Permission(models.Model):
    """ 权限表
        普通字段: id, url, feature
        关联字段:
    """

    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=64, verbose_name='正则URL')
    feature = models.CharField(max_length=16, verbose_name='功能')
    is_menu = models.BooleanField(verbose_name='是否显示在菜单内')

    group = models.ForeignKey(to='Group', to_field='id', verbose_name='权限组', blank=True)

    def __str__(self):
        return self.feature

    class Meta:
        verbose_name_plural = '权限表'


class Group(models.Model):
    """ 权限组表
        普通字段: id, title
        关联字段:
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16, verbose_name='权限组名')

    menu = models.ForeignKey(to='Menu', to_field='id', verbose_name='菜单', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '权限组表'


class Menu(models.Model):
    """ 菜单表
        普通字段: id, title
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16, verbose_name='菜单名')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '菜单表'

```


- 在version2/rbac/admin.py`文件内，在此版本中，为了项目测试方便，修改为使用sqlite数据库


```python
# version2/rbac/admin.py

from django.contrib import admin
from rbac import models

admin.site.register(models.Role)
admin.site.register(models.Permission)
admin.site.register(models.User)
admin.site.register(models.Group)
admin.site.register(models.Menu)
```

- 启动项目后，我们需要在新版本的项目中使用`python3 manage.py createsuperuser`命令创建管理员账号，登陆该账号，就可以在admin后台管理中插入数据了，插入的数据，读者可以使用管理员账号登录查看，也可自行创建管理员账号，直接打开数据库也是可以查看的
	- `ziawang`, `pass1234`



#### 2. 初始化用户权限
- 初始化用户权限应该在用户登陆成功之后，但是获取数据的过程与登录认证及中间件代码没有冲突，所以放在最前面写，同时还可以保证后面的连贯性。因为整个文档我是按照开发思路完成的

###### 2.1 设计数据结构
- 版本1中，初始化用户权限时完成了两个任务
	1. 将用户权限及权限相关的feature封装到permission_dict中，然后百村到session中
	2. 将用户的feature组成的列表保存到了feature_list中，然后保存到session中
- 在本版本中除了要完成上面两个任务之外，还要创建一种适合生成左侧菜单的数据结构，并且在左侧菜单中，我们不需要将每一个菜单下的组显示，只需要将菜单下所有组中的所有`is_menu=True`的权限显示在该菜单下即可。因此该数据结构最外层必须是一个字典，存放每一个菜单id与菜单内要显示的权限的信息，包括权限名、url、is_menu等

- 设计的数据结构如下

```python

{
	1: {
		"menu_id": 1,
		"menu_title": "数据管理"，
		"active": True/False,
		"children": [
			{"title": "图书列表", "url": "/showbooks/", "is_menu": True/False, "active": True/False}
		]
	}
	2: {
		...
	}
}

```

- 关于`active`
	- 在页面中，我们应该让当前路径以及当前路径所在的菜单，在页面中有不同的显示，这样才能让用户更清楚的知道自己在哪个位置，比如让菜单处于打开的状态，而其他菜单下的内容处于隐藏状态，对于链接，我们可以将它字体颜色变成红色。
	- 以上这些需求是**基于我们能够找到这个权限对应的a标签以及权限所属的菜单**上才能完成的。因此我们用一个变量标识这个权限对应的url，我们就可以对其进行操作。
	- 如果当前路径匹配到了权限组中的一个权限，并且这个权限的`is_menu=True`，那么我们就可以将该权限下的`active`值设置为`True`即可。


###### 2.2 获取数据
- **注意**
	- 在`init_permission`中，不建议直接在函数内就生成我们设计好的那种数据结构，我们只需要创建一种中间结构，等到要生成页面的时候再利用中间结构来生成目标数据结构，因为我们的`init_permision`函数是在`login`视图函数中被调用的，如果在登陆验证login函数中就将这所有的数据处理一次性完成完全没有必要，而且还**增加了功能之间的耦合性**。
	- 中间结构类型如下
		- 此处将`active`默认值设置为`False`

```
[
	{"menu_id": 1, "menu_title": "xxx", "title": "xxx", "url": "xxx", "active": False}
	{...}	
]

```



- 创建文件`version2/rbac/service/init_permission.py`文件，代码如下

```python
from django.conf import settings


def init_permission(user, request):
    """ 初始化用户权限，并将数据保存到session中(包括初始化菜单数据和用户权限数据)
    Args:
        user: 用户对象
        request: 请求对象
    Return: None
    """

    permissions = user.roles.values('permissions__url',
                                    'permissions__feature',
                                    'permissions__is_menu',
                                    'permissions__group_id',
                                    'permissions__group__menu__id',
                                    'permissions__group__menu__title'
                                    ).distinct()

    # 用户权限相关
    permission_dict = {'features': [], 'urls': []}
    for item in permissions:
        permission_dict['features'].append(item['permissions__feature'])
        permission_dict['urls'].append(item['permissions__url'])

    request.session[settings.FEATURE_LIST] = permission_dict['features']
    request.session[settings.PERMISSION_DICT] = permission_dict

    menu_list = []
    for item in permissions:
        tpl = {}
        if not item['permissions__is_menu']:
            continue
        tpl['menu_id'] = item['permissions__group__menu__id']
        tpl['menu_title'] = item['permissions__group__menu__title']
        tpl['feature'] = item['permissions__feature']
        tpl['url'] = item['permissions__url']
        tpl['active'] = False
        menu_list.append(tpl)

    request.session[settings.MENU_LIST] = menu_list
```

- 这里同样是要以`settings.py`中更的配置变量作为key存放value
- 目前`setting.py`中添加的配置如下

```python
FEATURE_LIST = 'feature list'

PERMISSION_DICT = 'permission dict'

MENU_DICT = 'menu dict'
```


#### 3. 中间件
- 在这个版本中，中间件的设计与版本1.0中的中间件是一样的，因为当前版本主要是修改数据库以及页面的显示

###### 3.1 配置白名单
- 在创建中间件之前，一定要配置白名单

```python
STATIC_URL = '/static/'

FEATURE_LIST = 'feature list'

PERMISSION_DICT = 'permission dict'

MENU_DICT = 'menu dict'

VALID_URLS = [
    '^/login/$',
    '^/admin.*/$'
]
```

###### 3.2 创建中间件

- 创建文件`version2/rbac/middlewares/loginmd.py`，代码如下

```python
# version2/rbac/middlewares/loginmd.py

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


class LoginMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        """ 对客户端请求进行session验证
            参数: request, 请求对象
            返回值： 1. None, 退出当前中间件，进入下一个中间件或视图函数
                    2. response响应对象, 不在继续下面的中间件或视图函数，而是将response直接返回给上一个中间件或WSGI
        """
        
        from django.conf import settings
        from django.shortcuts import redirect, HttpResponse
        import re

        # 验证url是否在白名单中
        current_url = request.path_info
        for url_regex in settings.VALID_URLS:
            if re.match(url_regex, current_url):
                return None

        # 验证session
        permission_dict = request.session.get(settings.PERMISSION_DICT)
        if not permission_dict:
            return redirect(to='/login/')

        # 验证权限
        flag = False
        for url in permission_dict['urls']:
            regex = f'^{url}$'
            if re.match(pattern=regex, string=current_url):
                flag = True
                break

        # 此处不return是为了存放其他逻辑

        if not flag:
            return HttpResponse('你没有该请求权限')

```

###### 3.3 配置中间件

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rbac.middlewares.loginmd.LoginMiddleWare',
]
```

#### 4 form组件
- form组件应该创建在项目的非rbac的应用中，因为rbac作为一个组件，其包含的功能应该要具有普适性，登录页面以及其对应的视图函数都不应该是rbac组件的一部分，因此我们将其放在项目`app`应用下。
- 创建文件`version2/app/service/forms.py`，代码如下

```python
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

#### 5. 视图函数
###### 5.1 配置路由
- 在创建视图函数之前，我们应该先将创建路由

```python
# version2/version2/urls.py

from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.login),
]
```


###### 5.2 在templates中创建login.html
- 代码如下

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

###### 5.3 login视图函数
- 视图函数写在了app应用下的views.py中，RBAC作为主键，在login视图函数中我们只需要在用户登陆验证成功之后嵌入组件中的初始化权限功能即可

```python
# version2/app/views.py

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
        if not form.is_valid():                                                 # 表单验证失败
            return render(request, 'login.html', {"form": form})
        else:                                                                   # 表单验证成功
            user_queryset = models.User.objects.filter(**form.cleaned_data)
            if not user_queryset:                                               # 用户在数据库中不存在
                form.add_error(field='password', error='用户名或密码错误')
                return render(request, 'login.html', {'form': form})
            else:                                                               # 用户在数据库中存在
                init_permission(user_queryset[0], request)                      # 初始化用户权限数据
                return redirect(to='/home/')

    elif request.method == 'GET':                                               # 为了增强程序的可扩展性，没有使用else
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
```

- 注意，这里对于判断`GET`请求使用的是`elif`而不是`else`处于两方面原因，方面，请求方法不光只有`GET`和`POST`（虽然其它的基本很少用），另一方面，当我们需要扩展对其他请求的处理时，else显然不合理，因此我选择使用`elif`


#### 6. 设计页面
- 当用户登陆成功之后，会跳转到包含其权限的home页面中。
- 到目前为止，我们在其session中存放了`permission_dict`, `feature_list`以及`menu_dict`。本节中，我们将使用`menu_dict`配合Django模板提供的`inclusion_tag`来生成一个menu菜单页面嵌入到base模板中，继承自它的模板页面将都能渲染出用户的权限菜单

 
###### 6.1 配置路由

```python
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.login),
    url(r'^home/$', views.home),
]

```


###### 6.2 创建base.html
- 不论我们进入到哪一个url路径对应的页面，左侧菜单都应该保持在指定的位置不变，它是所有页面都需要的部分，因此我们需要创建一个基模板来避免重复造轮子

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">
</head>
<body>
<div class="menu-left">
    {% block menu %}{% endblock %}
</div>

<div class="content">
    {% block content %}{% endblock %}
</div>

<script src="https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>
<script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>
```

- 这样创建的模板一丁点CSS样式都没有，我们需要为其添加样式，但是我们应该将css样式单独存放在一个文件中，并且文件应该存放在一个专门用来存放静态文件的文件夹下

###### 6.3 配置静态文件
- 接下来，我们在`version2/app/`创建一个static文件夹，并且我们还要在其文件夹下再创建一个名为`app`的文件下，然后我们在该文件夹下存放静态文件。
	- 为什么要这么做？ 每一个项目下的应用都有各自的静态文件，将这些静态文件存放在项目下同一个static文件中不利于项目的稳定运行，比如两个应用拥有相同名称的静态文件时，这样对于文件中的数据而言显然是不安全的，因此我们创建这样的结构，让每一个应用的static文件夹下再添加一个应用名文件夹，当调用静态文件时，同一个项目下的每一个应用名称都是独一无二的，因此静态文件的路径肯定而是独一无二的，这就避免的同名文件的冲突

```

——static
   └─app
	  └─  app.css

```

- `app.css`文件内容如下

```css

.menu-left{
    width: 20%;
    height: 500px;
    background-color: cadetblue;
    float: left;
}

.content{
    width: 80%;
    height: 500px;
    background-color: beige;
    float: left;
}

.hide{
    display: none;
}

a.active{
    color: red;
}
```

###### 6.4 创建自定义inclusion-tag
- inclusion-tag是Dajngo为我们提供的一种模板标签，我们可以自定义inclusion-tag。
- inclusion-tag可以渲染出一个html标签页面，并且该html数据可以用来嵌入到其他页面中。

1.  创建inclusion-tag
	- 我们需要在app下创建一个名称为`templatetags`的文件夹，并且**名称必须是这个**，然后在其中创建一个`.py`文件，文件名称可以自定义，然后在文件中导入`django.template`下的`Library`类来创建标签。代码如下

```python
# version2/app/templatetags/mytag.py
from django.template import Library
from django.conf import settings
from re import match

register = Library()


@register.inclusion_tag(filename='menu.html')
def menu_html(request):
    """生成一个菜单页面
    Args:
        request: 请求对象
    Return:
        context_dict: 一个上下文字典，存放用户渲染menu.html的数据
    """

    current_url = request.path_info
    menu_dict = {}
    menu_list = request.session.get(settings.MENU_LIST)
    for item in menu_list:
        menu_id = item['menu_id']
        menu_title = item['menu_title']
        title = item['feature']
        url = item['url']
        active = item['active']

        regex = f'^{url}$'
        if match(pattern=regex, string=current_url):							# 匹配当前路径对应权限并使用active标识
            active = True

        if menu_id in menu_dict:
            menu_dict[menu_id]['children'].append({"title": title, "url": url, "active": active})
            if active:
                menu_dict[menu_id]['active'] = True
        else:
            menu_dict[menu_id] = {
                "menu_id": menu_id,
                "menu_title": menu_title,
                "active": active,
                "children": [
                    {"title": title, "url": url, "active": active}
                ]
            }

    return {'menu_dict': menu_dict}
```

###### 6.5 创建menu.html
- inclusion_tag创建的自定义标签在调用时会将装饰器内filename指定的模板文件渲染成html数据，并嵌入到调用该inclusion_tag的模板中

- 我们将要创建的左侧菜单在`menu.html`中进行渲染，代码如下
- **注意**
	- `menu.html`既然要作为html的一部分数据内容嵌入到调用`menu_html`标签的HTML文件中，因此我们在`menu.html`中就不需要再声明`<html> <head> <body>`标签了

```html

<div class="item-menu">
    {% for menu in menu_dict.values %}
        <div class="menu-title">{{ menu.menu_title }}</div>
        {% if menu.active %}
            <div class="item-permission">
        {% else %}
            <div class="item-permission hide">
        {% endif %}
        {% for permission in menu.children %}
            {% if permission.active %}
            <p><a class="active" href="{{ permission.url }}">{{ permission.title }}</a></p>
            {% else %}
            <p><a href="{{ permission.url }}">{{ permission.title }}</a></p>
            {% endif %}
        {% endfor %}
    </div>
    </div>
    {% endfor %}
</div>
```

###### 6.6 创建js文件
- 我们应该让菜单能随意的张开和隐藏，在`vresion2/app/static/app/`目录下创建文件`app.js`文件

- 代码如下

```javascript
$('.menu-title').click(function () {
   if ($(this).next().hasClass('hide')){
       $(this).next().removeClass('hide');
   } else {
       $(this).next().addClass('hide');
   }
});
```

## 接下来？
- 好吧，第二个版本到此结束了，在这个版本中，我们修改了models中的模型，这主要是为了实现菜单的功能，还有一个要记住的就是**模型的设计至关重要**，他直接关系到功能的实现与否，要实现完整的功能，对数据库取出的数据处理成合适的结构也非常重要，往往字典+列表是我们组装数据结构中最常用到的模型
- 在接下来的版本中，我们将对左侧菜单进行更进一步的改进，实现在不同页面中保持权限对应超链接及div保持active状态，这也要修改一下模型

