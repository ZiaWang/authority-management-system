# RBAC Version1.0

## 介绍
- 在这个版本的rbac中，我们将完成一个最最简单的RBAC权限管理系统的雏形，它也是RBAC的核心思想


## 分析
- 对于Web项目来说，不同用户的权限本质上都是体现在对URL的访问权限上，比如某个用户有删除数据的权限，那么他就有访问该URL的权限，当服务器接收到该用户发起的URL请求时，会根据其请求中包含的信息进行相应的处理，反之，用户不具有该权限的时候，即使其向服务器发起了该URL请求，该URL请求也会被服务器重定向或者其他方式与请求发起者交互。

- 因此，在Web开发中，权限经常对应的就是一个个url地址，我们需要将权限、用户、角色分别设计成数据表，并根据他们之间的关系进行关联处理。

## 设计

#### 表结构设计
###### 表结构分析
- 权限表与角色表之间应该为多对多关系。一个角色可以拥有多种权限，同样的一种权限可以对应多个角色。这就好比一个图书管理员拥有"增加书籍"，"阅读书籍"等权限，而"阅读书籍"权限可以对应管理员，也可以对应读者、老师等等
- 角色表与用户表之间在本项目中设置成多对多关系。由于在有的体系中，用户与角色之间有的是多对一，而在可以一人身兼多职这种体系结构中，多对多也是允许的。
	- 设计成多对多的另一个好处就是，他可以兼容多对一的关系，使得程序具有较强的扩展性

###### 字段分析
- 用户表
	- 用户表要存放用户用来登录的用户名和密码，因此存放username和password两个必要字段
	
- 权限表
	- 权限表中除了代表权限的url之外，还要有一个字段，用来代表权限对应的功能，这样我们在渲染模板的时候，只需判断该功能是否在用户权限下就可以选择性的显示其权限内的功能了。
	- 至于为什么要添加feature字段，除了上面解释之外，另外还考虑到了url的可变性（需要对包含正则表达式的url进一步处理），对于类似编辑、删除权限的路径，都需要将其对应的在数据库中的id传入，这样才能准确的操作数据库中指定的一条记录。
	- 在这里选择将数据库中记录的id使用正则表达式嵌入到路径中，主要是考虑到了操作上的方便和功能上的扩展。这样可以精准的操作数据库中指定的一条记录，并且可以操作指定范围内的记录，如果使用`/del/?id=xxx`的形式，不利于功能上的实现（比如批量操作记录）

- 角色表
	- 角色表中主要是角色的id及角色名称。

- 由于是多对多关系，因此我们需要创建额外的两张表来存储多对多关系。

###### 结构
- 权限表(Permission)

```
id			url			feature
1		/books/			showbooks
2		/add/   		  add
3		/del/(\d+)/		delbook

...

```

- 角色表(Role)

```
id 			title
1			admin
2			reader	
...

```


- 用户表(User)

```
id			username		pasword
1			ziawang			pass
2			jay				passjay
...
```

- 权限&角色表(Permission_Role)

```
id			permission_id		role_id
1				1					1
2				1					2
3				2					1
....
```

- 用户&角色表(User_Role)

```
id			User		Role
1			 1			 1
2			 1			 2
3			 2			 1
...

```



#### 项目目录结构

```bash

└─version1
    ├─ manage.py
    │
    │
    ├─app
    │  │  admin.py
    │  │  apps.py
    │  │  models.py
    │  │  tests.py
    │  │  views.py
    │  │  __init__.py
    │  │
    │  └──migrations
    │        __init__.py
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
    │  └─migrations
    │          __init__.py
    │
    ├─templates
    └─version1
        │  settings.py
        │  urls.py
        │  wsgi.py
        └─ __init__.py 

```



###### 注意
- 在创建完项目目录之后，一定要记得去项目目录下的`setting.py`中注册项目应用，这里的应用注册方式与旧版本有些差别
	- 在新版本中，每一个应用下都会产生一个`apps.py`的文件，包含了对app的配置接口，我们只需要将其中定义的类的**类名**注册到`settings.py`中即可
	- 在旧版本中，我们需要在`settings.py`中将**应用名**（注意与新版本的区别）注册即可

```python
# version1/version1/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.apps.AppConfig',
    'rbac.apps.RbacConfig'
]

```

```python
# /version1/rbac/apps.py

from django.apps import AppConfig


class RbacConfig(AppConfig):
    name = 'rbac'

```



## 开始撸代码
#### 1. models.py
- 要实现一个RBAC，首先我们需要创造权限，没有权限，谈啥都是白搭，当然还哟有与权限相关角色、用户，因此项目的第一步就是创建数据库。
- Django本身自带的ORM框架可以帮助我们快速的实现数据库的设计，在ORM中，数据库中的表体现为面向对象中的类，所有的类都是继承自`models.Model`类，而类的静态属性就对应表中的字段，所有的字段都是通过`models`来创建的。
- 代码如下

```python
# version1/rbac/models.py

from django.db import models


class User(models.Model):
    """ 用户表
        普通字段: id, username, password
        关联字段： roles(多对多)
    """
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')

    roles = models.ManyToManyField(to='Role', verbose_name='角色', blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户表'


class Permission(models.Model):
    """ 权限表
        普通字段: id, url, feature
    """
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=64, verbose_name='正则URL')
    feature = models.CharField(max_length=16, verbose_name='功能')

    def __str__(self):
        return self.feature

    class Meta:
        verbose_name_plural = '权限表'


class Role(models.Model):
    """ 角色表
        普通字段： id, ,title
        关联字段： permissions(多对多)
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16, verbose_name='角色名')

    permissions = models.ManyToManyField(to='Permission', verbose_name='权限', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '角色表'
```

###### 1.1 配置后台管理

- 本项目中，为了方便，我们使用Django自带的admin后台管理来录入数据，因此需要在代码中进行相关配置如下
	- 对ManyToMany关联的字段使用了`blank=True`，这样我们就可以在不为一条记录选择关联字段的情况下，在后台中录入数据。**但是要注意的是，blank作用的只是Django的后台管理中数据的录入**，这等于是Django为了我们录入数据方便，提供了一个可以这样操作的接口，在数据库中这种操作是绝对不允许的，数据库主键表中的关联字段必须要优先于外键表中的记录产生，这样才会有数据提供给外键表中的记录选择
	- 使用`__str__`方法是为了格式化输出记录对象(其实就是Model类的一个实例)
	- 在类`Meta`中定义`verbose_name_plural` 参数可以让数据表在admin后台中按照该参数指定的字符串显示，可读性更好，其作用类似于`verbosr_name`

- 要想让models中的表能够在admin后台显示，以上操作还不够，我们需要修改rbac应用下的models文件，将模型类注册到`admin.site`对象上

```python
# version1/rbac/admin.py

from django.contrib import admin
from rbac import models


admin.site.register(models.Permission)
admin.site.register(models.User)
admin.site.register(models.Role)
```

###### 1.2 配置数据库

- 做完上述步骤之后，我们要将`models.py`中的模型类迁移到rbac应用的migrations目录下，并且生成数据库中的表，然后在这之前，我们先在项目目录下的`setting.py`中配置数据库

```python
# version1/version1/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ziawang',
        'HOST': 'localhost',
        'POST': 3306,
        'USER': 'root',
        'PASSWORD': 'pass'
    }
}
```


###### 1.3 兼容数据库接口(pymysql, mysqldb)


- 配置完数据库之后，我们还要修改ORM使用的模块，在Django中，ORM要与要与数据库进行交互，就必须通过python的`mysqldb`或者`pymysql`来实现，在python2中，使用的是`mysqldb`，而在python3中，使用的就是`pymysql`。Django的ORM默认使用mysqldb，因此我们需要在rbac的`__init__`文件中使用pymysql模块的`install_as_mysqldb`方法即可。
	- **注意**，这里之所以要在rbac下的`__init__`文件中可以让rbac组件的兼容性更好，另外，如果你使用的是python2的话，这段代码要删掉

```python
# /version1/rbac/__init__.py

import pymysql

pymysql.install_as_MySQLdb()
```

- 然后我们再在数据库中创建setting下DATABASES中`NAME`对应的数据库

```mysql
mysql> create database ziawang;
Query OK, 1 row affected (0.03 sec)

mysql> use ziawang;
Database changed
mysql>
```

###### 1.4 迁移与生成表

- 使用命令`python3 manage.py makemigrations`将`models.py`中的模型类迁移到rbac应用的migrations目录下。然后再使用`python3 manage.py migrate`在数据库中创建表。在一大串的`......OK`之后，我们的表就在数据库中生成了

```mysql
mysql> show tables;
+----------------------------+
| Tables_in_ziawang          |
+----------------------------+
| auth_group                 |
| auth_group_permissions     |
| auth_permission            |
| auth_user                  |
| auth_user_groups           |
| auth_user_user_permissions |
| django_admin_log           |
| django_content_type        |
| django_migrations          |
| django_session             |
| rbac_permission            |
| rbac_role                  |
| rbac_role_permissions      |
| rbac_user                  |
| rbac_user_roles            |
+----------------------------+
15 rows in set (0.00 sec)

mysql>
```

###### 1.5 录入数据

- 要想去admin后台管理中录入数据，首先你要有一个admin账号，因此我们使用`python3 manage.py createsuperuser`创建一个admin用户，启动Django服务器之后，浏览器输入`127.0.0.1:8000/admin/`就可以进入登陆界面了，然后录入你的数据



[admin_login_page](https://github.com/ZiaWang/authority-management-system/blob/master/img/admin_login_page.png?raw=true)


[admin_home_page](https://github.com/ZiaWang/authority-management-system/blob/master/img/admin_home.png?raw=true)


- 数据如下

```mysql
mysql> select * from rbac_role;
+----+--------+
| id | title  |
+----+--------+
|  1 | 馆长   |
|  2 | 管理员 |
|  3 | 老师   |
|  4 | 学生   |
+----+--------+
4 rows in set (0.03 sec)

mysql> select * from rbac_role_permissions;
+----+---------+---------------+
| id | role_id | permission_id |
+----+---------+---------------+
|  1 |       1 |             1 |
|  2 |       1 |             2 |
|  3 |       1 |             3 |
|  4 |       1 |             4 |
|  5 |       2 |             1 |
|  6 |       2 |             2 |
|  7 |       2 |             4 |
|  8 |       3 |             1 |
|  9 |       3 |             2 |
| 10 |       4 |             1 |
+----+---------+---------------+
10 rows in set (0.00 sec)

mysql> select * from rbac_user;
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | ziawang  | pass     |
|  2 | gz       | pass     |
|  3 | admin    | pass     |
|  4 | tc       | pass     |
+----+----------+----------+
4 rows in set (0.00 sec)

mysql> select * from rbac_user_roles;
+----+---------+---------+
| id | user_id | role_id |
+----+---------+---------+
|  1 |       1 |       4 |
|  2 |       2 |       1 |
|  3 |       3 |       2 |
|  4 |       4 |       3 |
+----+---------+---------+
4 rows in set (0.00 sec)

mysql> select * from rbac_permission;
+----+------------------+-----------+
| id | url              | feature   |
+----+------------------+-----------+
|  1 | /showbooks/      | showbooks |
|  2 | /addbook/        | addbook   |
|  3 | /delbook/(\d+)/  | delbook   |
|  4 | /editbook/(\d+)/ | editbook  |
+----+------------------+-----------+
4 rows in set (0.00 sec)

mysql>
```


- 至此，数据库创建的工作在此版本中结束了，接下来是用户登陆验证的代码实现


#### 2. 获取用户权限
- 当一个用户登录之后，我们可以将该用户所具有的权限及其他信息保存在request对象的session中，这是一个可以独立封装的功能，因此我们应该将其功能封装并放在一个模块中

###### 2.1 数据结构
- 对数据结构的设计和存取贯穿整个在整个项目中，**保存在session中的数据需要有利于我们功能的实现，并且能保证性能**。因此选择字典以及列表搭配的方式封装数据，模型如下

```python
{
	features: [xxx, xxx, xxx],
	urls: [xxx, xxx, xxx]
}

```

- 这样，当用户登陆成功后，urls中存放了其权限范围内的url，features中存放了权限对应的功能名称。

###### 2.2 获取数据
- 创建`version1/rbac/service/init_permission.py`，代码如下

```python
from django.conf import settings


def init_permission(user, request):
    """ 获取用户权限并初始化，并将数据保存到session中
        参数:
            user: 用户对象
            request: 请求对象
        返回值: None
    """
    permissions = user.roles.values('permissions__url' , 'permissions__feature')
    permission_dict = {'features': [], 'urls': []}
    for item in permissions:
        permission_dict['features'].append(item['permissions__feature'])
        permission_dict['urls'].append(item['permissions__url'])

    request.session[settings.FEATURE_LIST] = permission_dict['features']
    request.session[settings.PERMISSION_DICT] = permission_dict

```

- 为了增强代码的可塑性和可扩展性，在项目`settings.py`中，声明配置变量，将该配置变量作为session的key存放数据。在导入数据的时候，使用`from django.conf import settings`即可，因为从`django.conf`导入的settings.py就将项目目录下的settings.py的内容包含了

```python
# version1/version1/settings.py

PERMISSION_DICT = 'permission dict for current user'			# 字符串内容随意

FEATURE_LIST = 'feature list'
```


#### 3. 创建中间件
- 中间件本质上就是一个类，在Django的生命周期中，请求通过WSGI之后，就会经过中间件，中间件像一个个过滤请求的管道，每一个请求经过中间件都需要被中间件进行处理

###### 3.1 创建url白名单
- 中间件会对所有经过其的请求进行处理，但有时候我们需要将有些请求中的路径不需要经过验证就能到达视图函数，比如登陆页面，因此我们需要将一些url放到白名单，避免出现“重定向次数过多的错误”（这个错误其实就是由于客户端GET请求获取页面时是没有携带session的，因为此时还没有登陆成功，于是验证失败，重定向到`/login/`，陷入死循环）。
- 白名单的配置应该像`permission_dict`一样保存在`settings.py`中，`settings.py`配置如下

```python
# version1/version1/settings.py

VALID_URLS = [
    '^login$',
    '^admin.*'
]                       # 白名单
```

###### 3.2 创建中间件类
- 定义一个中间件类，需要继承自Django中的一个类，并且强烈建议将该类的内容拷贝到我们自定义的中间件同一模板文件下，或者自定义的文件下，这样即使在Django其他版本将基类名称或者其他内容进行修改了，我们仍然可以保证中间件继承自基类。可以提高rbac组件的健壮性和兼容性
- 创建文件`version1/rbac/middlewares/loginmd.py`，代码如下

```python
# version1/rbac/middlewares/loginmd.py
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



#### 4. 创建form组件
- 在创建完权限初始化和中间件之后，我们就可以创建页面了，创建登录页面我们需要用到Django为我们提供的From组件
- 创建Form组件其实就是自定义一个继承自Form的类，因此我们可以将其封装到一个模块中。
- 创建文件`version1/app/service/forms.py`，代码如下
- 注意，为了实现功能的解耦，forms文件应存放到app应用目录下

```python
# version1/app/service/forms.py

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

- 定义form组件的字段时要注意，字段的名称将会成为form子标签的`name`属性的值，因此我们应始终保持字段名与模型中字段名相同，这样可以免去不必要的麻烦



#### 5. 创建login视图函数
- 表单组件既可以用来生成标签，可以用来初始化标签，也可以用来验证客户端表单提交的内容，在视图函数中，我们至少要有两个逻辑
	1. 如果请求方法为`GET`，我们应该使用form组件，让Django帮我们渲染一个login页面返回给客户端
	2. 如果请求方法为`POST`，我们应该先验证客户端POST提交的数据的合法性
		1. 如果数据合法，将进行舒适化函数，初始化用户权限
		2. 如果数据不合法，将form中生成的错误信息渲染到页面中返回
- 在app应用下的views.py中，代码如下

```python
# /version1/app/views.py

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
```


#### 6. 创建模板
###### login
- 在项目的template目录下创建模板`login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">
</head>
<body>

<form action="/login/" method="post" novalidate>
    {% csrf_token %}
    <p>username: {{ form.username }} {{ form.errors.username.0 }}</p>
    <p>password: {{ form.password }} {{ form.errors.password.0 }}</p>
    <input type="submit" value="登陆">
</form>


<script src="https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>
<script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>
```

###### home.html
- 创建`home.html`
- 这里简单的实现将每位用户权限内的url做成`a`超链接标签显示在页面上。因此需要在模板页面上进行判断，比如下面这种形式

```html

{% if "showbooks" in request.feature_list %}
	<a gref="/showbooks/">图书列表</a>

```

- 但是这样显然在url非常多的情况下会重复造轮子，我们其实可以将功能封装到一个类中，然后通过该类的方法去实现上述功能。
	- 用类实现的时候，我们创建的基类可以只拥有公共的方法，对于不同类的feature可以继承并派生出不同的方法，比如`BasePagePermission`可以扩展出`BaseBookPermission`和`BaseOrderPermission`等

- 创建文件`/version1/rbac/service/basepage.py`，代码如下

```python
# /version1/rbac/service/basepage.py

class BasePagePermission:
    def __init__(self, feature_list):
        self.feature_list = feature_list

    def has_home(self):
        if 'home' in self.feature_list:
            return True


class BaseBookPermission(BasePagePermission):
    def has_showbooks(self):
        if 'showbooks' in self.feature_list:
            return True

    def has_addbook(self):
        if 'addbook' in self.feature_list:
            return True

    def has_delbook(self):
        if 'delbook' in self.feature_list:
            return True

    def has_editbook(self):
        if 'editbook' in self.feature_list:
            return True
```

- 在渲染模板`home.html`之前，我们需要先完善下`urls.py`中的配置

```python
# version1/version1/urls.py

from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.login),
    url(r'^home/$', views.home),
]
```

- 接下来就是去模板`home.html`中进行操作，代码如下

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">
</head>
<body>

{% if page_permission.has_showbooks %}
    <p><a href="">主页</a></p>
{% endif %}

{% if page_permission.has_showbooks %}
    <p><a href="">图书列表</a></p>
{% endif %}

{% if page_permission.has_addbook %}
    <p><a href="">增加图书</a></p>
{% endif %}

{% if page_permission.has_delbook %}
    <p><a href="">删除图书</a></p>
{% endif %}

{% if page_permission.has_editbook %}
    <p><a href="">编辑图书</a></p>
{% endif %}

<script src="https://cdn.bootcss.com/jquery/3.2.1/jquery.min.js"></script>
<script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</body>
</html>
```

- `/home/`对应的视图函数home

```python

def home(request):
    """ 返回用户主页面，包含用户权限
        参数: request, 用户当前请求对象
        返回值: 响应对象，将home.html渲染完成后作为响应体内容返回
    """
    feature_list = request.session[settings.FEATURE_LIST]
    page_permission = BaseBookPermission(feature_list)
    return render(request, 'home.html', {'page_permission': page_permission})
```


## 总结

#### 评价
- 至此，最最简单的一个RBAC版本完成了。它不但界面丑陋，而且功能上实际上是不完善的，他只包含了最基本的权限管理，当然也是权限管理的核心————"用户通过与角色的关联来间接的获取指定权限"

#### 现在的rbac应用下都有什么
###### 初始化功能
- `version1/rbac/service/init_permission.py`
	1. 从数据库获取数据，并处理
	2. 将`features`通过配置变量封装到session中
	3. 将`permission_dict`通过配置比俺俩封装到session中
 
- 在下一版本中，将会对其进行扩展，因为这里只实现了将用户权限显示在页面，没有菜单，产品经理肯定要和你拼命

###### 中间件
- 中间件到目前为止，主要执行三个功能
	1. 验证url是否在白名单中
		- 是，进入下一中间件或者视图函数
		- 否，进入下一个验证
	2. 验证请求是否存在对应的session
		- 是，进入下一个验证
		- 否，重定向到登录界面
	3. 验证请求中url路径是否在用户权限中
		- 是，进入下一中间件或者视图函数
		- 否，返回响应`HttpResponse('权限不够')`

###### models
- 我们创建了三个模型类，在数据库中就存在了五张表，他们是RBAC权限管理的基础
- 后面版本中会对模型类进行不断的修正和丰富，以满足更多功能的需要

###### basepagepermission.py
- 这个文件我选择创建在rbac应用下，因为我觉得这个功能对于每一个rbac组件都是必要的，除非你想一个个硬编码设计home页面的渲染

###### admin.py
- 这里现在只注册了三个模型类，后续还会增加

#### 项目中我们配置了什么
###### settings.py
- `DATABASES`
- `MIDDLEWARE`
- `INSTALLED_APPS`
- `VALID_URLS` 白名单
- `PERMISSION_DICT` 权限字典
- `FEATURE_LIST` 用户权限对应的功能列表
 
###### version1/app/views.py
- 不同项目的应用是不一样的，其视图函数也肯定不一样，因此我们应该将视图函数存放在其他应用中如`version1/app/views.py`

###### version1/app/forms.py
- 针对`views.py`中的视图函数，我们需要在该app目录下而不是rbac应用下创建form组件类。


#### 接下来？
- 这个版本只是个雏形，接下来我们会一步步的，一个版本一个版本的实现一个真正的RBAC权限管理系统组件
- 在下一个版本中，我们将实现左侧菜单，这就需要我们对数据库进行修改，因为要显示的页面上的数据是来自数据库的，我们要想在页面上显示菜单以及其他东西就必须从数据库来入手！








