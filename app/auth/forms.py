# -*-coding:utf-8-*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,BooleanField, PasswordField

from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email=StringField(u'邮箱',validators=[Required(),Length(1,64), Email()])
    password=PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登陆') 

class RegistrationForm(Form):
    email=StringField(u'注册邮箱',validators=[Required(),Length(1,64), Email()])
    username=StringField(u'用户名',validators=[Required(),Length(1,64), Regexp('^[A-Za-z][A-Za-z0-_.]*$', 0, u'用户名必须是邮箱或者')])
    password=PasswordField(u'密码', validators=[Required()])
    password2=PasswordField(u'确认密码', validators=[Required(),EqualTo('password',message=u'请确认密码一致')])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册')

class ChangePasswordForm(Form):    #这个是登陆了修改密码
    old_password = PasswordField(u'旧密码',validators=[Required()])
    password=PasswordField(u'请输入新密码',validators=[Required()])
    password2=PasswordField(u'请确认新密码',validators=[Required(), EqualTo('password', message=u'请确认密码一致')])
    submit=SubmitField(u'修改密码')

class PasswordResetRequestForm(Form):
    email=StringField(u'邮箱',validators=[Required(), Email(), Length(1,64)])
    submit=SubmitField(u'重置密码')

class PasswordResetForm(Form):       #这个是忘记密码
    email=StringField(u'用户邮箱',validators=[Required(), Email(), Length(1,64)])
    password=PasswordField(u'请输入新密码',validators=[Required()])
    password2=PasswordField(u'请确认新密码',validators=[Required(), EqualTo('password', message=u'请确认密码一致')])
    submit=SubmitField(u'重置密码')
    
class ChangeEmailForm(Form):
    email=StringField(u'新邮箱', validators=[Required(), Email(),Length(1,64)])
    password=PasswordField(u'用户密码', validators=[Required()])
    submit=SubmitField(u'更改邮箱')
    
    def validate_email(self,field):             #这个函数厉害自动执行
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'设置的邮箱已被注册') 
