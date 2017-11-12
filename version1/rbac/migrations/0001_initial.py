# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-11 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=64, verbose_name='正则URL')),
                ('feature', models.CharField(max_length=16, verbose_name='功能')),
            ],
            options={
                'verbose_name_plural': '权限表',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=16, verbose_name='角色名')),
                ('permissions', models.ManyToManyField(blank=True, to='rbac.Permission', verbose_name='权限')),
            ],
            options={
                'verbose_name_plural': '角色表',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
                ('roles', models.ManyToManyField(blank=True, to='rbac.Role', verbose_name='角色')),
            ],
            options={
                'verbose_name_plural': '用户表',
            },
        ),
    ]
