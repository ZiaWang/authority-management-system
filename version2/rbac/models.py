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
