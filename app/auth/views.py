# -*-coding:utf-8-*-
from flask import render_template, request, url_for,flash,redirect
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from flask.ext.login import logout_user, login_required, login_user,current_user
from ..email import send_email

@auth.route('/login',methods=['GET', 'POST'])#这里路由虽然是从/开始，但是是相对路径来的，因为在blueprint中指定了登记路由的起始根路径
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)    #用户自己实现，记住登陆用的,这里就是
            return redirect(request.args.get('next') or url_for('main.index'))   #这里的reques的next不知干嘛的,
        flash(u'请输入正确的账号和密码')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout(): 
    logout_user()
    flash(u'成功退出')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)       #添加到数据库
        db.session.commit()        #先提交，因为这里要先用id
        token=user.generate_confirmation_token()  #根据id生成令牌
        send_email(user.email, u'邮箱验证', 'auth/email/confirm',user=user,token=token)                     #发送令牌连接
        flash(u'已发送邮箱验证邮件，请查收完成验证')
        #flash(u'注册成功')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

#确认账户
@auth.route('/confirm/<token>')      #处理认证链接
@login_required                      #我觉得在认证时自动登陆是这里搞的鬼
def confirm(token):
    if current_user.confirmed:                   #防止多次点击
        return redirect(url_for('main.index'))  #已经验证过了
    if current_user.confirm(token):
        flash(u'验证通过')   #到时加个验证成功后自动本次登陆，，加入这个功能后上面先判confirmed的才有实际意义
        print current_user.confirmed   #这句有起作用的，测试用的
    else:
        flash(u'验证连接无效或过期了')
    return redirect(url_for('main.index'))
#对上面有个疑问，就是还没登陆，没执行login loader user，，那current_user还没有confirmed的吧，即原始默认对象，
#下面还来个在请求之前的处理，钩子函数,使用要很小心，涉及所有请求，问题出现了，就算是，我登陆了一个没有认证的账号，，后台加入的，就出现点击主页，会跳转到‘auth/unconfirmed.html’，，这样就达到书中所说的筛选认证的，，跳到这来的，有两种情况，注册了的
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:      #所以认证后登陆了，过了这关,
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5]!='auth.' and request.endpoint!='static':
            #flash(u'还没验证')
            #print current_user.confirmed    #测试用的，不知是不是重新登陆
            return redirect(url_for('auth.unconfirmed'))
    #return redirect(url_for('main.index'))本来想着解决验证成功后可以立即登陆，，可是不行，想着在验证后

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#重新发送认证//从设计来讲，上面的unconfirmed.html中应该有confirm的链接导向这个处理函数
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()  
    send_email(current_user.email, u'邮箱验证', 'auth/email/confirm',user=current_user,token=token) 
    flash(u'验证邮件已重新发送')
    return redirect(url_for('main.index'))

@auth.route('/change-password',methods=['GET', 'POST'])
@login_required
def change_password():
    form=ChangePasswordForm()
    print 'hello'
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data   #修改提交
            db.session.add(current_user)
            flash(u'您的密码已经修改成功')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码不正确')
    return render_template('auth/change_password.html', form=form)

@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    if not current_user.is_anonymous:          #未登录的才可以，已登陆了的可以通过修改，不用重置
         return redirect(url_for(main.index))
    form=PasswordResetRequestForm()               #这里需要表单一是重置的邮箱，二十，一个提交按钮，从post来个链接
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:                              
            token=user.generate_reset_token()
            send_email(user.email, u'重置您的密码','auth/email/reset_password',user=user,token=token,next=request.args.get('next'))#这个next也还不知道
            flash(u'重置密码的邮件已经发送，请查收完成重置')   #还没有注册的的账号也这样显示吗？
            return redirect(url_for('auth.login'))
        flash(u'账号还没注册')    #这个是我添加的
    return render_template('auth/reset_password.html',form=form)
#一般一个功能设计，这里分三种情况，未认证账户，认证了的账户，认证了的GET，认证了的POST，要重置当然是默认没登陆的情况了

@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    if not current_user.is_anonymous:    #结合之前的知识，，必须是发送完认证邮件后重新点击认证连接登陆的
        return redirect(url_for('main.index'))
    form=PasswordResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash(u'密码修改成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '邮箱地址更改认证',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash(u'修改邮箱的认证邮件已发往您的新邮箱')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码不正确')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(u'邮箱地址更改成功')
    else:
        flash(u'邮箱更改失败')
    return redirect(url_for('main.index'))
