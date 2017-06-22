# -*-coding=UTF-8-*-

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from ansible_api import MyTask
from passet.models import Setting, Asset, PGroup
from django.db.models import Q
from django.contrib.auth.models import  Group
from pigeon.api import *
from ansible_api import MyRunner
from django.contrib.auth.decorators import login_required
from pigeon.settings import BASE_DIR

import subprocess

def get_account_env(department, env):
    groups = PGroup.objects.filter(Q(department=department),Q(env=env))
    assets = []
    for group in groups:
        assets += group.asset_set.all()
    account = len(assets)
    return account

    

@login_required
def index(request):
    departments = request.user.groups.all()
    infos = []
    for department in departments:

        account_dev = get_account_env(department, 'dev')
        account_pre = get_account_env(department, 'pre')
        account_pro = get_account_env(department, 'pro')
        groups = PGroup.objects.filter(Q(department=department), Q(manager=request.user))
        info = {'department':department, 'account_dev':account_dev, 'account_pre':account_pre, 'account_pro':account_pro, 'groups':groups}
        infos.append(info)
	
    return render(request,'pansible/config.html',locals())

@login_required
def editgroup(request):
    departments = request.user.groups.all()
    infos = []
    select_id = 1
    for department in departments:
        groups = PGroup.objects.filter(Q(department=department),Q(gtype=1), Q(manager=request.user))
        select_id += 1
        assets = []
        for group in groups:
            assets += group.asset_set.all()
        info = {'department':department, 'assets':assets, 'select_id':select_id}
        infos.append(info)
        if request.method == "POST":
            depart = request.POST.get('depart')
            if depart != department.name:
                continue
            name = request.POST.get('groupname','')
            iplist = request.POST.getlist('assetlist','')
            assetlist = [Asset.objects.get(ip=ip) for ip in iplist ]
            comment = request.POST.get('comment','')
            editgroup = PGroup(name=name, department=department, gtype=2, comment=comment)
            editgroup.save()
            editgroup.manager.add(request.user)
            assets_for_log = []
            for asset in assetlist:
                assets_for_log.append(asset.ip)
                insert_group = PGroup.objects.filter(name=name)
                for group in insert_group:
                    asset.group.add(group)
                    asset.save()
            msg = '%s 创建了 %s部门的资产组 %s，资产包含%s'%(request.user, department, name.encode("utf-8"), assets_for_log)
            set_action_log(msg)
    return render(request,'pansible/editgroup.html',locals())


def gen_resource(assets):
    res = []
    setting = Setting.objects.get(name='default')
    username = setting.user
    password = setting.passwd
    for asset in assets:
        ip = asset.ip
        hostname = asset.hostname
        port = asset.port
        info = {'hostname':hostname, 'ip':ip, 'port':port, 'username':username, 'password':password}
        res.append(info)
    return res

@login_required
def task(request):
    departments = request.user.groups.all()
    infos = []
    for department in departments:
        groups = PGroup.objects.filter(Q(department=department), Q(manager=request.user))
        assets = []
        asset_all_in_group = PGroup.objects.filter(Q(department=department),Q(gtype=1),Q(manager=request.user))
        for group in asset_all_in_group:
            assets += group.asset_set.all()#该组内所有asset
        info = {'department':department, 'groups':groups, 'assets':assets}
        infos.append(info)
        
    if request.method == 'POST':
        order = request.POST.get('order')
        cmd = order.split(" ",1)
        deny_cmd = ['reboot','rm','kill','pkill','shutdown','half','mv','dd','mkfs','>','wget']
        if not order:
            return render(request,'pansible/task.html',locals())
        if cmd [0] in deny_cmd:
            error = u'%s命令被限制，无法执行'%(order)
            return render(request,'pansible/task.html',locals())
        ip_select = request.POST.getlist('assets','')
        depart = request.POST.get('depart')
        group_select = request.POST.getlist('groups','')
        groups_asset_select = [PGroup.objects.get(id=gro) for gro in group_select]
        assets_group_select = []
        for group_asset_select in groups_asset_select:
            for asset_in_group in group_asset_select.asset_set.all():
                assets_group_select.append(asset_in_group)
        asset_select = [ Asset.objects.get(ip=ip_s) for ip_s in ip_select ]
        assets_final = list(set(asset_select)|set(assets_group_select))
        
        resource = gen_resource(assets_final)
        cmd = MyTask(resource)
        result = cmd.hello(order)
        if type(result) == str:
            #error = result
            error = "输入命令格式有误，请检查重新输入。"
            return render(request,'pansible/task.html',locals()) 
        result_ok = result.get('ok').items()
        result_failed = result.get('failed').items()
        result_dark = result.get('dark').items()
        
        msg = '%s 对 %s部门的资产组 %s执行了 %s操作，结果为 %s'%(request.user, depart.encode("utf-8"), assets_final, order.encode("utf-8"), result)
        set_action_log(msg)
    return render(request,'pansible/task.html',locals())

@login_required
def change_self_group(request):
    gid = request.GET.get('id')
    group = PGroup.objects.get(id=gid)
    assets_old = group.asset_set.all()
    department = group.department
    pgroup = PGroup.objects.get(Q(department=department),Q(gtype=1),Q(manager=request.user))
    asset_all = pgroup.asset_set.all()
    if request.method == 'POST':
        value = request.POST.getlist('assetlist')
        comment = request.POST.get('comment')
        groupname = request.POST.get('groupname')
        group.name = groupname
        group.comment = comment
        group.save()
        asset_new = [Asset.objects.get(ip=va) for va in value]
        for asset in assets_old:
            if asset not in asset_new:
                asset.group.remove(group)
        for asset in asset_new:
            if asset not in assets_old:
                asset.group.add(group)
    return render(request,'pansible/change_self_group.html',locals())

@login_required
def deletegroup(request):
    gid = request.GET.get('id')
    PGroup.objects.get(id=gid).delete()
   
    response = HttpResponseRedirect('/pansible/config')
    return response

@login_required
def upload(request):
    departments = request.user.groups.all()
    infos = []
    for department in departments:
        groups = PGroup.objects.filter(Q(department=department), Q(manager=request.user))
        assets = []
        asset_all_in_group = PGroup.objects.filter(Q(department=department),Q(gtype=1),Q(manager=request.user))
        for group in asset_all_in_group:
            assets += group.asset_set.all()
        info = {'department':department, 'groups':groups, 'assets':assets}
        infos.append(info)
    if request.method == "POST":
        target_dir = request.POST.get('target_dir')
        file_name = request.FILES.get('file_name')
        target_file_dir = os.path.join(target_dir, file_name.name)
        if not file_name:
            return render(request, 'pansible/copy.html', locals())
        # = os.path.join(BASE_DIR, 'file')
        #file_path = os.path.join(BASE_DIR, file_name)
        file_path = '/tmp/%s' % (file_name)
        with open(file_path, 'w') as f:
            for chunk in file_name.chunks():
                f.write(chunk)
        
        ip_select = request.POST.getlist('assets', '')
        group_select = request.POST.getlist('groups', '')
        depart = request.POST.get('depart')
        groups_asset_select = [PGroup.objects.get(id=gro) for gro in group_select]
        assets_group_select = []
        for group_asset_select in groups_asset_select:
            for asset_in_group in group_asset_select.asset_set.all():
                assets_group_select.append(asset_in_group)

        asset_select = [ Asset.objects.get(ip=ip_s) for ip_s in ip_select ]
        assets_final = list(set(asset_select)|set(assets_group_select))
        
        res = gen_resource(assets_final)
        runner = MyRunner(res)
        runner.run("command", module_args='mkdir -p %s'%(target_dir), become=True)
        runner.run('copy', module_args='src=%s dest=%s backup="yes" directory_mode' % (file_path, target_dir), pattern='*', become=True)
        ret = runner.results
        result_ok = ret.get('ok').items()
        result_failed = ret.get('failed').items()
        result_dark = ret.get('dark').items()

        msg = '%s 对 %s部门的资产组 %s执行了 %s的文件分发，结果为 %s'%(request.user, depart.encode("utf-8"), assets_final, file_name, ret)
        set_action_log(msg)
        subprocess.call('sudo rm -rf %s'%(file_path),shell=True)
    return render(request,'pansible/copy.html',locals())

