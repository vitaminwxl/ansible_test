# coding: utf-8
from settings import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import time



def set_action_log(content, filename='pigeon_action.log'):
    """ 
    return a log file object
    根据提示设置log打印
    """
    log_file = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(log_file):
        os.mknod(log_file)
        os.chmod(log_file, 0777)
    output = open(log_file, "a")
    try:
        time_format = '%Y-%m-%d %X'
        time_now = time.strftime(time_format, time.localtime(time.time()))
        msg = "%s - %s" % (time_now, content)
        #msg = msg.encode('utf-8')
        output.write(msg)
        output.write("\n")
    finally:
        output.close()


def require_admin():
    """
    """

    def _deco(func):
        def __deco(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('login'))
					
            if request.user.is_superuser != 1:
                return HttpResponseRedirect(reverse('index'))
            return func(request, *args, **kwargs)

        return __deco

    return _deco
