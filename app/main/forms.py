# -*-coding:utf-8-*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,BooleanField, PasswordField,TextAreaField, SelectField

from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role
from flask.ext.pagedown.fields import PageDownField

class NameForm(Form):
    name=StringField(u'想写点什么...', validators=[Required()])
    submit=SubmitField(u'提交')

class EditProfileForm(Form):
    name=StringField(u'真实姓名',validators=[Length(0,64)])
    location=StringField(u'我在',validators=[Length(0,64)])
    about_me=TextAreaField(u'关于')
    submit=SubmitField(u'保存')

class EditProfileAdminForm(Form):
    email=StringField(u'邮箱', validators=[Required(), Length(1,64),Email()])
    username=StringField(u'用户名',validators=[Required(),Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'用户名必须是之母开头，只含有字母数字和下划线')])
    confirmed=BooleanField(u'认证')
    role=SelectField(u'角色', coerce=int)
    name=StringField(u'姓名',validators=[Length(0,64)])
    location=StringField(u'位置', validators=[Length(0,64)])
    about_me=TextAreaField(u'关于我')
    submit=SubmitField(u'保存资料')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices=[(role.id, role.name) for role in Role.query.order_by(Role.name).all()]#d对应表单的选择列表
        self.user=user   #这个设计用来admin对其他用户的管理的
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter(email=field.data).first():
            raise ValidationError(u'这个邮箱已被注册了')
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter(username=field.data).first():
            raise ValidationError(u'这个用户名已被注册了')

class PostForm(Form):
    body=PageDownField(u'想写点什么...', validators=[Required()])
    submit=SubmitField(u'提交')

class CommentForm(Form):
    body=PageDownField('', validators=[Required()])
    submit=SubmitField(u'提交')

     
