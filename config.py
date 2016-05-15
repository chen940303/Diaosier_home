#coding:utf-8
import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    #SQLALCHEMY_ON_REARDOWN = True这句错了
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_MAIL_SENDER='447325059@qq.com'
    FLASKY_ADMIN= os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE=20
    FLASKY_FOLLOWERS_PER_PAGE=20
    FLASKY_COMMENTS_PER_PAGE=20
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIMEOUT = 0.5
    
    @staticmethod
    def init_app(app):
        pass
    
class DevelopmentConfig(Config):
    DEBUG=True
    MAIL_SERVER= 'smtp.qq.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME= os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URL') or 'sqlite:////'+os.path.join(basedir,'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED=False     #测试时不开启加密，测试客户端处理不用复杂
    SQLALCHEMY_DATABASE_URI=os.environ.get('TES_DATABASE_URL') or 'sqlite:////'+os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:////'+os.path.join(basedir, 'data.sqlite')
    
    @classmethod
    def init_app(cls,app):
        Config.init_app(app)
        import logging
        from logging.handlers import SMTPHandler
        credentials=None
        secure=None
        if getattr(cls,'MAIL_USE_TLS',None) is not None:
            credentials=(cls.MAIL_USE_TLS,None)
            if getarrt(cls, 'MAIL_USE_TLS',None):
                secure()
        mali_handler=SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT), fromaddr=cls.FLASKY_MAIL_SENDER,toaddrs=[cls.FLASKY_ADMIN],subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',credentials=credentials,secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        # 输出到 stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

config={'development':DevelopmentConfig,
        'testing':TestingConfig,
         'production':ProductionConfig,
       'default':DevelopmentConfig    
        }
