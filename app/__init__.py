# -*-coding:utf-8-*-
from flask import Flask , render_template, session, url_for, redirect, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
import os
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.mail import Mail, Message
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown

bootstrap=Bootstrap()
mail=Mail()
moment=Moment()
db=SQLAlchemy()
login_manager=LoginManager()
login_manager.session_protection="strong"
login_manager.login_view = 'auth.login'  #我猜这个是@login_required有关
pagedown=PageDown()

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])  #整个配置对象加载进来
    config[config_name].init_app(app)
     
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)                   #是没有初始化login_manager才导致current_user不能用的
    pagedown.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)         #根目录
    #附加路由和自定义错误页面
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')#路由前缀
    from api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')    

    return app
