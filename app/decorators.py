#-*-coding:utf-8-*-
from functools import wraps
from flask import abort
from flask.ext.login import current_user
from models import Permission

def permission_required(permission):    #用于检查权限，就像检查登陆一样
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)            #程序如果这里出错中断，跳转
            return f(*args, **kwargs)
        return decorated_function
    return decorator
#闭包开发做修饰器，带参数返回两层，

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)  
#检查了administer
