# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-03 23:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('passet', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Group',
            new_name='PGroup',
        ),
        migrations.AlterModelTable(
            name='pgroup',
            table='p_group',
        ),
    ]
