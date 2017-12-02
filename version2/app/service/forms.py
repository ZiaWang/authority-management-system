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
