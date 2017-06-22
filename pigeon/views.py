#-*-coding=UTF-8-*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from validateLDAPLogin import LDAPLogin

@login_required()
def index(request):
    print request.session.get('role_id')
    if request.method == 'GET':
        username = request.user.username
    return render(request,'index.html',locals())


def Login(request):
    try:
        admin_user = User.objects.get(username='admin')
    except:
        admin_user = User(username='admin')
    admin_user.set_password('vitamin20')
    admin_user.is_superuser=1
    admin_user.save()
    """登录界面"""
    error = ''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'GET':
        return render_to_response('login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
        # 过滤初始密码
            if password == 'Gome123.cOm':
                error = "不被允许的密码，初始密码请先修改"
                return render_to_response('login.html', {'error': error})

            if username != "admin":
            # LDAP 验证
                login_status = LDAPLogin(username, password)
                if login_status != "success":
                    error = login_status
                    return render_to_response('login.html', {'error': error})

            # 判断该用户是否存在
            is_exists = User.objects.filter(username=username).exists()
            if not is_exists:
                error = "没有授权该系统权限，请联系运维申请该权限"
                return render_to_response('login.html', {'error': error})
            # 判断该用户是否是第一次登录
            user_reset = User.objects.get(username=username)
            if user_reset.last_login == user_reset.date_joined:
                # 第一次登录，重设密码为LDAP密码，admin除外
                if username != "admin":
                    user_reset.set_password(password)
                    user_reset.save()

            # 本机验证
            user = authenticate(username=username, password=password)
            if user is None:
                if username != "admin":
                    # LDAP验证成功后，密码不正确则修改密码
                    user_reset.set_password(password)
                    user_reset.save()
                else:
                    error = "用户名密码不正确"
                    return render_to_response('login.html', {'error': error})

            # 重设密码后再次验证
            user = authenticate(username=username, password=password)
            if user.is_active:
                login(request, user)
                
                if user.is_superuser:
                    request.session['role_id'] = 2
                else:
                    request.session['role_id'] = 1
                
                return HttpResponseRedirect(request.session.get('pre_url', '/'))
            else:
                error = '用户未激活'
        else:
            error = '用户名或密码错误'
    return render_to_response('login.html', {'error': error})

def Logout(request):
    logout(request)
    return HttpResponseRedirect('/')
