# -*-coding=UTF-8-*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class PGroup(models.Model):
    name = models.CharField(max_length=80)
    department = models.CharField(max_length=80)
    segment = models.CharField(max_length=160)
    env = models.CharField(max_length=80)
    manager = models.ManyToManyField(User, blank=True, verbose_name=u"管理员")
    gtype = models.CharField(max_length=80)
    comment = models.CharField(max_length=160, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_tablespace = 'p_group'



class Asset(models.Model):
    ip = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"主机IP")
    port = models.IntegerField(blank=True, null=True, verbose_name=u"端口号")
    hostname = models.CharField(unique=True, max_length=128, verbose_name=u"主机名")
    group = models.ManyToManyField(PGroup, blank=True, verbose_name=u"所属组")

    def __unicode__(self):
        return self.ip

    class Meta:
        db_tablespace = 'asset'

class Setting(models.Model):
    name = models.CharField(max_length=100)
    user = models.CharField(max_length=100, null=True, blank=True)
    passwd = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_tablespace = 'setting'
