# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-06 02:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passet', '0006_setting'),
    ]

    operations = [
        migrations.AddField(
            model_name='pgroup',
            name='comment',
            field=models.CharField(max_length=160, null=True),
        ),
    ]
