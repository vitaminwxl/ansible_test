# -*-coding=UTF-8-*-

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from pigeon.api import *
from passet.asset_api import get_all_asset_info
from passet.models import Asset
import ConfigParser
from pigeon.settings import BASE_DIR
from pansible.ansible_api import MyRunner

@require_admin()
def index(request):
    return render(request,'pssh/pssh_show.html')

@require_admin()
def edit(request):
    ip_infos = get_all_asset_info()
    assets = [ip_info[0] for ip_info in ip_infos]
    cf = ConfigParser.ConfigParser()
    config = os.path.join(BASE_DIR, 'hosts_allow_deny.conf')
    cf.read(config)
    sec = cf.sections()
    default = cf.items('default')
    if request.method == 'POST':
        target_ips = request.POST.getlist('assets')
        allow_ips = request.POST.get('allow')
        allow_ips_list = allow_ips.split(',')
        deny_ips = request.POST.get('deny')
        deny_ips_list = deny_ips.split(',')
        option_del = request.POST.get('option_del')
        if option_del:
            for target_ip in target_ips:
                if target_ip not in sec:
                    continue
                else:
                     if allow_ips:
                         for allow_ip in allow_ips_list:
                             cf.remove_option(target_ip,allow_ip)
                     if deny_ips :
                         for deny_ip in deny_ips_list:
                             cf.remove_option(target_ip,deny_ip)
                cf.write(open(config,'w'))
        else:
            for target_ip in target_ips:
                if target_ip not in sec:
                    cf.add_section(target_ip)
                if allow_ips:
                    for allow_ip in allow_ips_list:
                        cf.set(target_ip,allow_ip,'allow')
                    print '插入成功'
                if deny_ips:
                    for deny_ip in deny_ips_list:
                        cf.set(target_ip,deny_ip,'deny')
                    print '插入成功'
                cf.write(open(config,'w'))
        allow_deny_go(target_ips)
    return render(request,'pssh/conf_edit.html',locals())

def allow_deny_go(targets):
    cf = ConfigParser.ConfigParser()
    config = os.path.join(BASE_DIR, 'hosts_allow_deny.conf')
    cf.read(config)
    '''
    allow_go = []
    deny_go = []
    default_conf = cf.items('default')
    for item in default_conf:
        if item[1] == 'allow':
            allow_go.append(item[0])
        if item[1] == 'deny':
            deny_go.append(item[0])
    '''

    for target_ip in targets:
        allow_go = []
        deny_go = []
        default_conf = cf.items('default')
        for item in default_conf:
            if item[1] == 'allow':
                allow_go.append(item[0])
            if item[1] == 'deny':
                deny_go.append(item[0])
        print target_ip
        try:
            add_conf = cf.items(target_ip)
            for item in add_conf:
                if item[1] == 'allow':
                    allow_go.append(item[0])
                if item[1] == 'deny':
                    deny_go.append(item[0])
        except:
            print 'none self conf'
        conf_go(target_ip,allow_go,'allow')
        conf_go(target_ip,deny_go,'deny')
	
def conf_go(target,ips_go,is_allow):
    file_name = '%s_hosts.%s'%(target,is_allow)
    file_dir = os.path.join(BASE_DIR, 'docs/%s'%(file_name))
    
    file_go = open(file_dir,'w')
    for ip in ips_go:
        message = 'sshd:%s:%s'%(ip,is_allow)
        file_go.write(message)
        file_go.write('\n')
    file_go.close()
    res =  [{"hostname": "127.0.0.1","ip":u'127.0.0.1', "port": "22", "username": "xiaolong", "password": "258258",},]
    runner = MyRunner(res)
    runner.run('copy', module_args='src=%s dest=%s backup="yes" directory_mode' % (file_dir, '/tmp/%s'%(file_name)), pattern='*')
    ret = runner.results
    print ret
    
def all_conf_go():
    ip_infos = get_all_asset_info()
    all_assets = [ip_info[0] for ip_info in ip_infos]
    allow_deny_go(all_assets)

@require_admin()
def detail(request):
    return render(request,'pssh/conf_search.html')
