# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-06 03:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='spiderkeyTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
                ('keyWordNum', models.IntegerField()),
                ('modifiedTime', models.CharField(max_length=50)),
                ('startTime', models.DateTimeField()),
            ],
            options={
                'db_table': 'spiderKey',
            },
        ),
        migrations.CreateModel(
            name='taskTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=100)),
                ('domain', models.CharField(max_length=50)),
                ('keyword', models.CharField(max_length=50)),
                ('taskCreateDate', models.DateTimeField()),
                ('subscribeStatus', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'pushTask',
            },
        ),
        migrations.AddField(
            model_name='spiderkeytable',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hello.taskTable'),
        ),
    ]
