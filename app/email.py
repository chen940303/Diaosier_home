# -*-coding:utf-8-*-
import os
from threading import Thread
from flask.ext.mail import  Message
from . import mail
from flask import current_app,render_template
#from ..manage import app

#原来的app换成current_app
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    #app_context =current_app.app_context()
    #app_context.push()  我就说要在这里修改点什么
    app = current_app._get_current_object()   #原来要加这句的
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body=render_template(template+'.txt', **kwargs)
    msg.html=render_template(template+'.html', **kwargs)
    thr=Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
