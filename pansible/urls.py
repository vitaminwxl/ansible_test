"""pigeon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^config/$',views.index,name='pansi_config'),
	url(r'^editgroup/$',views.editgroup,name='pansi_editgroup'),
	url(r'^task/$',views.task,name='pansi_task'),
	url(r'^copy/$',views.upload,name='pansi_copy'),
	url(r'^config/edit/$',views.change_self_group,name='change_self_group'),
	url(r'^config/del/$',views.deletegroup,name='delete_group'),
]
