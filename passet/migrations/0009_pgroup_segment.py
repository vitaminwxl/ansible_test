# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-12-30 16:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passet', '0008_auto_20161216_1215'),
    ]

    operations = [
        migrations.AddField(
            model_name='pgroup',
            name='segment',
            field=models.CharField(default='127.0.0.1', max_length=160),
            preserve_default=False,
        ),
    ]
