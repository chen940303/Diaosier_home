#-*-coding:utf-8-*-
from functools import wraps
from flask import g
from flask.ext.login import current_user
from ..models import Permission

def permission_required(permission):    #用于检查权限，就像检查登陆一样
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return fobidden(u'没有权限')            #程序如果这里出错中断，跳转
            return f(*args, **kwargs)
        return decorated_function
    return decorator
