# -*-coding=UTF-8-*-
import ConfigParser
import IPy
from IPy import IP
import MySQLdb
from django.contrib.auth.models import User, Group
from models import Asset, PGroup
from django.conf import settings
from pigeon.settings import BASE_DIR
import os,django
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pigeon.settings")# project_name 项目名称
#django.setup()

###############################
###############################


def get_all_asset_info():
    conn = MySQLdb.connect(host='10.69.213.48',user='jump_sel',db='jumpserver',passwd='g0M7R14a',port=3306)
    cursor = conn.cursor()
    sql = "select ip, port, hostname from jasset_asset"
    cursor.execute(sql)
    asset_all = cursor.fetchall()
    return asset_all

def delete_ip(group_id, segments):
    group_old = PGroup.objects.get(id=group_id)
    asset_old = group_old.asset_set.all()
    asset_all = get_all_asset_info()
    ip_required = []
    for segment in segments:
        for ip in IPy.IP(segment):
            ip_required.append(str(ip))
    for asset in asset_old:

        if asset.ip not in [asset_info[0] for asset_info in asset_all]:
            asset.delete()
            continue
        elif asset.ip not in ip_required:
            asset.delete()

def delete_user_department():
    cf = ConfigParser.ConfigParser()
    config = os.path.join(BASE_DIR, 'group.conf')
    cf.read(config)
    groups = cf.sections()
    user_department = []
    conf_users = []
    for group in groups:
        manager = cf.get(group,"manager")
        department = cf.get(group,"department")
        conf_users.append(manager)
        info = {manager, department}
        user_department.append(info)
    users = User.objects.all()
    for user in users:
        #u_groups = user.groups.all()
        if user.username not in conf_users:
            if user.is_superuser != 1:
                user.delete()
                continue
        u_groups = user.groups.all()
        for u in u_groups:
            if {user.username,u.name} not in user_department:
                user.groups.remove(u)
    return True



def check_ip(ip_list):
    # 检查ip_list内元素是否为网段或IP
    result = True
    for ip in ip_list:
        try:
		    print IPy.IP(ip)
        except:
            result = False
    
    return result

def check_conf():
    error = ''
    try:
        cf = ConfigParser.ConfigParser()
        cf.read("group.conf")
    except:
        error =  'config does not exist!'
    groups = cf.sections()
    if len(set(groups)) != len(groups):
        error =  'groupname error!'
    for group in groups:
        segments = cf.get(group,"segment").split(",")
        manager = cf.get(group,"manager").split(",")
        department = cf.get(group,"department")
        env = cf.get(group,"env")
        if env not in ['pro', 'pre', 'dev']:
            error = 'env error'
    return error
    

def add_group():
    # 从zeus数据库获取所有asset列表 asset_all
    # 通过网段过滤出group的ip列表 插入或者更新数据库
    # 同时需要更新config
    cf = ConfigParser.ConfigParser()
    cf.read("segment.conf")
    segment = cf.get("segment","test")
    ip_group = []
    for ip in ip_all:
        if ip in IPy.IP(segment):
            ip_group.append(ip)

def initialise_new():
    groups = PGroup.objects.filter(gtype=1)
    asset_all = get_all_asset_info()
    for group in groups:
        group_id = group.id
        #asset_all_old = group.asset_set.all()
        segments = group.segment.split(',')
        delete_ip(group_id, segments)
        for segment in segments:
            for asset in asset_all:#asset (ip,port,hostname)
                if asset[0] in IPy.IP(segment):
                    if Asset.objects.filter(ip=asset[0]):
                        asset = Asset.objects.get(ip=asset[0])
                        asset_groups_obj = PGroup.objects.filter(id=group_id)
                        asset.group = asset_groups_obj
                        asset.save()
                        continue
                    new_asset = Asset(ip=asset[0], port=asset[1],hostname=asset[2])
                    new_asset.save()
                    asset_groups_obj = PGroup.objects.filter(id=group_id)
                    new_asset.group = asset_groups_obj
                    new_asset.save()
                    

def initialise():
    # 从zeus数据库获取所有asset列表 asset_all
    # 读config 匹配对应的每个部门分组的网段进行更新
    #
    error = check_conf()
    if not error:
        print 'good'
    else:
        print error
    print 'start initialise'
    cf = ConfigParser.ConfigParser()
    config = os.path.join(BASE_DIR, 'group.conf')
    cf.read(config)
    groups = cf.sections()
    pgroups = PGroup.objects.filter(gtype=1)
    for pg in pgroups:
        if pg.name not in groups:
            pg.delete()
    asset_all = get_all_asset_info()
    delete_user_department()
    for group in groups:
        ip_group = []
        segments = cf.get(group,"segment").split(",")
        managers = cf.get(group,"manager").split(",")
        department = cf.get(group,"department")
        env = cf.get(group,"env")
        if not Group.objects.filter(name=department):
            dgroup = Group(name=department)
            dgroup.save()
        for manager in managers:
            if not User.objects.filter(username=manager):
                user = User(username=manager)
                user.save()
                obj_group = Group.objects.filter(name=department)
                user.groups = obj_group
                user.save()
            else:
                user = User.objects.get(username=manager)
                obj_group = Group.objects.get(name=department)
                user.groups.add(obj_group)
                user.save()

        if PGroup.objects.filter(name=group):
            PGS = PGroup.objects.get(name=group)
            PGS.department = department
            PGS.env = env
            old_manager_users = PGS.manager.all()
            for o in old_manager_users:
                if o.username not in managers:
                    PGS.manager.remove(o)
            for manager in managers:
                m_user = User.objects.get(username=manager)
                PGS.manager.add(m_user)
            
            PGS.save()
            group_id = PGS.id
        else:
            addpgroup = PGroup(name=group,department=department,env=env,gtype=1)
            addpgroup.save()
            for manager in managers:
                m_user = User.objects.get(username=manager)
                addpgroup.manager.add(m_user)
            addpgroup.save()
            group_id = addpgroup.id
        ###删除多余ip
        delete_ip(group_id, segments)
        ###1.在Zeus中不存在的；2.在网段中不存在的
        for segment in segments:
            for asset in asset_all:#asset (ip,port,hostname)
                if asset[0] in IPy.IP(segment):
                    if Asset.objects.filter(ip=asset[0]):
                        asset = Asset.objects.get(ip=asset[0])
                        asset_groups_obj = PGroup.objects.filter(id=group_id)
                        asset.group = asset_groups_obj
                        asset.save()
                        continue
                    new_asset = Asset(ip=asset[0], port=asset[1],hostname=asset[2])
                    new_asset.save()
                    asset_groups_obj = PGroup.objects.filter(id=group_id)
                    new_asset.group = asset_groups_obj
                    new_asset.save()
                    ip_group.append(asset[0])
    print 'initialise finished'
    return True
   
