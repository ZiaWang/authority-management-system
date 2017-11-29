from django.db import models


class User(models.Model):
    """ 用户表
    普通字段:
        id, username, password
    关联字段：
        roles(多对多)
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
    普通字段:
        id, url, feature
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
    普通字段：
        id, ,title
    关联字段：
        permissions(多对多)
    """

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=16, verbose_name='角色名')

    permissions = models.ManyToManyField(to='Permission', verbose_name='权限', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '角色表'