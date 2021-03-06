# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-06-24 21:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_auto_20200624_2103'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_goods_num', models.IntegerField(default=1)),
                ('c_is_select', models.BooleanField(default=True)),
                ('c_goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.Goods')),
                ('c_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='App.Customer')),
            ],
        ),
    ]
