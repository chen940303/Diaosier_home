#-*-coding:utf-8-*-
from flask import jsonify
from . import api
from ..exceptions import ValidationError

def forbidden(message):
    response=jsonify({'error':'forbidden','message':message})
    response.status_code=403
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])    #定义全局处理出错函数，就像flask提供的http状态码一样

def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response

