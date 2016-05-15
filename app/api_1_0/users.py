#-*-coding:utf-8-*-
from . import api
from flask import request, g, url_for,jsonify,url_for
from ..models import Post,Permission
from .authentication import auth
from .. import db
from .decorators import permission_required


@api.route('/user/<int:id>')
@auth.login_required
def get_user(id):
    pass

@api.route('/user/',methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_user():
    pass
