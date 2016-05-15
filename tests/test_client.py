#-*-coding:utf-8-*-
import unittest
from app import create_app, db
from app.models import User, Role
from flask import url_for
import re

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client=self.app.test_client(use_cookies=True)
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response=self.client.get(url_for('main.index'))
        self.assertTrue(u'你好' in response.get_data(as_text=True))

    def test_register_and_login(self):
        #注册测试
        response=self.client.get(url_for('auth.register'))
        print response.status_code
        response=self.client.post(url_for('auth.register'),data={'email':'gdutccm@163.com','username':'gdutccm','pwssword':'123456','password2':'123456'}, follow_redirects=True)#注册的post没成功，，后台没响应
        print response.status_code
        user=User.query.filter_by(email='gdutccm@163.com').first() #这两句是加的
        print user
        self.assertTrue(response.status_code==200)#测试这里有问题，打印是200，，应该是重定向的原因,因为允许了重定向，由于post不成功，所以回到了get
        #登陆
    def test_login(self):
        response=self.client.post(url_for('auth.login'),data={'email':'gdutccm@163.com','password':'123456'},follow_redirects=True)
        print response.status_code       #调试打印
        data=response.get_data(as_text=True)
        self.assertTrue(re.search(u'gdutccm',data))
        #print data                          #调试打印
        self.assertTrue(u'登陆' in data)  #这句不知是不是views中的，是的这response是post的html页面，和get不同
        #发送验证，通过路径名传递验证指令
        #db.session.commit(),然而，我加了这句也没用
        user=User.query.filter_by(email='gdutccm@163.com').first()    #单元测试说这个没有找到用户,应该就是注册创建时没有session.add有效
        print user
        token=user.generate_confirmation_token()
        response=self.client.get(url_for('auth.comfirm',token=token),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue(u'验证通过',data)
        #退出
        response=self.client.get(url_for('auth.logout'),follw_redirects=True)
        data==response.get_data(as_text=True)
        self.assertTrue(u'成功退出')
