#-*-coding:utf-8-*-
from flask.ext.httpauth import HTTPBasicAuth
from .errors import forbidden, unauthorized
from ..models import User,Role,AnonymousUser
from flask import jsonify,g
from . import api

auth=HTTPBasicAuth()

##生成rest web服务api的模块

@auth.verify_password   #认证密码，，每次请求都有
def verify_password(email_or_token,password):
    if email_or_token=='':
        g.current_user=AnonymousUser()
        return True
    if password=='':
        g.current_user=User.verify_auth_token(email_or_token)  #修改成支持令牌认证
        g.token_used=True
        return g.current_user is not None
    user=User.query.filter_by(email=email_or_token).first()
    if not user:
       return False
    g.token_used=False
    g.current_user=user
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

@api.before_request
@auth.login_required
def befor_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden(u'Unconfirmed account 账户未认证')

@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600),'expiration':3600})


