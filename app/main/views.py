# -*-coding:utf-8-*-
from datetime import datetime
from flask import render_template ,session ,redirect, url_for, flash,request,current_app,make_response,abort
from flask.ext.login import current_user, login_required  #这个需要吗，有用吗
from . import main
from .forms import NameForm,EditProfileForm, EditProfileAdminForm,PostForm,CommentForm
from .. import db
from ..models import User, Role, Permission, Post, Comment
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    show_followed=False
    form=PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post=Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        flash(u'提交成功')
        return redirect(url_for('.index'))
    page=request.args.get('page', 1, type=int)
    if current_user.is_authenticated:
        show_followed=bool(request.cookies.get('show_followed',''))
    if show_followed:
        query=current_user.followed_posts
    else:
        query=Post.query
    pagination=query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False) #这句
    posts=pagination.items  
    return render_template('index.html', current_time=datetime.utcnow(), posts=posts, form=form, pagination=pagination, show_followed=show_followed)

@main.route('/all')
@login_required
def show_all():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp=make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

@main.route('/user/<username>')
def user(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts=user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)    #个人资料
@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash(u'用户资料保存成功')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data=current_user.name 
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)

@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'用户资料保存成功')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post=Post.query.get_or_404(id)
    form=CommentForm()
    if form.validate_on_submit():
        comment=Comment(body=form.body.data, post=post,author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'评论成功')
        return redirect(url_for('.post',id=post.id,page=-1))
    page=request.args.get('page',1,type=int)
    if page ==-1:
        page=(post.comments.count()-1)/current_app.config['FLASKY_COMMENTS_PER_PAGE']+1
    pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments=pagination.items
    return render_template('post.html', posts = [post],form=form,comments=comments,pagination=pagination)

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user!=post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        flash(u'文章编辑成功')
        return redirect(url_for('.post',id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u'没有该用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注他了')
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    flash(u'关注 %s 成功'% username)
    return redirect(url_for('.user',username=username))

@main.route('/followers/<username>')
def followers(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u"不合法用户")
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followers.paginate(page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
    follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title=u"关注他的人", endpoint='.followers',pagination=pagination,follows=follows)

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u'没有该用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'你没有关注他')
        return redirect(url_for('.user',username=username))
    current_user.unfollow(user)
    flash(u'取消关注 %s 成功'% username)
    return redirect(url_for('.user',username=username))

@main.route('/followed-by/<username>')
def followed_by(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash(u"没有该用户")
        return redirect(url_for('.index'))
    page=request.args.get('page',1,type=int)
    pagination=user.followed.paginate(page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
    follows=[{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,title=u"关注的人", endpoint='.followed_by',pagination=pagination,follows=follows)

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page=request.args.get('page',1,type=int)
    pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(page,per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],error_out=False)
    comments=pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment=Comment.query.get_or_404(id)
    comment.disabled=False
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment=Comment.query.get_or_404(id)
    comment.disabled=True
    db.session.add(comment)
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))

#数据库缓慢的查询语句记录下来，写入日志
from flask.ext.sqlalchemy import get_debug_queries
@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration>=current_app.config["FLASKY_SLOW_DB_QUERY_TIMEOUT"]:
            current_app.logger.warning('Slow query:%s\nParameters:%s\nDuration:%f\nContext:%s\n' % 3(query.statement,query.parameters,query.duration,query.context))
    return response

