#-*-coding=UTF-8-*-

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from pigeon.api import *
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect

@require_admin()
def index(request):
    users = User.objects.all()
    return render(request,'puser/puser_show.html',locals())

def delete_user(request):
    user_id = request.GET.get('id')
    user_del = User.objects.get(id=user_id)
    user_del.delete()
    response = HttpResponseRedirect('/puser')
    msg = "%s 删除了平台用户 %s "%(request.user, user_del)
    set_action_log(msg)
    return response

@require_admin()
def manager_remove(request):
    user_id = request.GET.get('id')
    user_target = User.objects.get(id=user_id)
    user_target.is_superuser = 0
    user_target.save()
    
    response = HttpResponseRedirect('/puser')
    msg = "%s 撤销了 %s 的平台管理员权限"%(request.user, user_target)
    set_action_log(msg)
    return response

@require_admin()
def manager_appoint(request):
    user_id = request.GET.get('id')
    user_target = User.objects.get(id=user_id)
    user_target.is_superuser = 1
    user_target.save()
    response = HttpResponseRedirect('/puser')
    msg = "%s 赋予了 %s 平台管理员权限"%(request.user, user_target)
    set_action_log(msg)
    return response
