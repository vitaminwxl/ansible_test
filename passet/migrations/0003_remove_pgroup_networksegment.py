# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-04 03:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('passet', '0002_auto_20161103_2330'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pgroup',
            name='networksegment',
        ),
    ]
