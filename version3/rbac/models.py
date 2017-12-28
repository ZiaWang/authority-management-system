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

    group_menu = models.ForeignKey(to='Permission', to_field='id', verbose_name='组内菜单', null=True, blank=True, on_delete=models.CASCADE)
    group = models.ForeignKey(to='Group', to_field='id', verbose_name='所属权限组', on_delete=models.CASCADE)

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

    menu = models.ForeignKey(to='Menu', to_field='id', verbose_name='所属菜单', on_delete=models.CASCADE)

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
