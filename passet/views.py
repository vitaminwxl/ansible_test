# -*-coding=UTF-8-*-

import ConfigParser
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pigeon.api import *
import hashlib
from asset_api import  initialise_new, check_ip
from django.contrib.auth.models import User, Group
from models import PGroup, Setting
from django.contrib.auth.decorators import login_required
from pigeon.settings import BASE_DIR
import os

@require_admin()
def index(request):
    #if request.method == 'GET':
    #    initialise()
    groups = PGroup.objects.filter(gtype=1)
    if request.method == "POST":
        user = request.POST.get('username','')
        passwd = request.POST.get('password','')
        
        if user and passwd:
            if Setting.objects.filter(name='default'):
                Setting.objects.filter(name='default').update(user=user, passwd=passwd)
                print 'change passwd success'
            else:
                Setting.objects.create(name='default',user=user,passwd=passwd)
            print 'have user and pass'
    return render(request,'passet/asset_show.html',locals())

def reset(request):
    initialise_new()
    response = HttpResponseRedirect('/passet')
    return response

def delete_group(request):
    gid = request.GET.get('id')
    pgroup = PGroup.objects.get(id=gid)
    pgroup.delete()
    msg = "%s 删除了资产组 %s ."%(request.user, pgroup)
    set_action_log(msg)
    response = HttpResponseRedirect('/passet')
    return response

def insert_group(request):
    
    if request.method == 'POST':
        groupname = request.POST.get('name')
        segment = request.POST.get('segment')
        if not segment:
            return render(request, 'passet/insert_group.html', locals())
        result = check_ip(segment.split(','))
        if  result == False:
            error = "维护标准格式不正确，请输入网段或IP"
            return render(request, 'passet/insert_group.html', locals())
        department = request.POST.get('department')
        env = request.POST.get('env')
        manager_str = request.POST.get('manager')
        managers = manager_str.split(',')
        if not PGroup.objects.filter(name=groupname):
            if not Group.objects.filter(name=department):
                group = Group(name=department)
                group.save()
            pgroup = PGroup(name=groupname, segment=segment, department=department, env=env, gtype=1)
            pgroup.save()
            for manager in managers:
                if not User.objects.filter(username=manager):
                    user = User(username=manager)
                    user.save()
                    group_obj = Group.objects.filter(name=department)
                    user.groups = group_obj
                    user.save()
                else:
                    user = User.objects.get(username=manager)
                    group_obj = Group.objects.get(name=department)
                    user.groups.add(group_obj)
                    user.save()
                pgroup.manager.add(user)
        initialise_new()
        msg = "%s 新建了资产组 %s ，维护标准为 %s ,部门为 %s ,环境为 %s ，管理员为 %s ."%(request.user, groupname.encode("utf-8"), segment.encode("utf-8"), department.encode("utf-8"), env.encode("utf-8"), manager_str.encode("utf-8"))
        set_action_log(msg)
        response = HttpResponseRedirect('/passet')
        return response
    return render(request, 'passet/insert_group.html',locals())

@require_admin()
def change_group_info(request):
    gid = request.GET.get('id')
    group = PGroup.objects.get(id=gid)
    depart_group = Group.objects.get(name=group.department)
    if request.method == 'POST':
        manager_all_old = [m for m in group.manager.all()]
        new_managers_str = request.POST.get('manager')
        segment = request.POST.get('segment')
        if not segment:
            return render(request, 'passet/insert_group.html', locals())
        result = check_ip(segment.split(','))
        if  result == False:
            error = "维护标准格式不正确，请输入网段或IP"
            return render(request, 'passet/insert_group.html', locals())
        group.segment=segment
        group.save()
        new_managers = new_managers_str.split(',')
        for mao in manager_all_old:
            if mao.username not in new_managers:
                group.manager.remove(mao)
        for nm in new_managers:
            if not User.objects.filter(username=nm):
                user = User(username=nm)
                user.save()
                user.groups = depart_group
                user.save()
            else:
                user = User.objects.get(username=nm)
                user.groups.add(depart_group)
                user.save()
            group.manager.add(user)
        initialise_new()
        response = HttpResponseRedirect('/passet')
        msg = "%s 编辑了资产组 %s ，将管理员改为 %s ."%(request.user, group, new_managers_str.encode("utf-8"))
        set_action_log(msg)
        return response
    return render(request,'passet/change_group_info.html',locals())
	
