# -*- coding: utf-8 -*-
# @Author : 13706
# @File : config.py
# @Project: ShareBill
# @CreateTime : 2021/5/9 12:31:38

class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = '@#$%Yzndmm0902'
    url = 'localhost'
    database = 'xiaopin'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:3306/%s' % (user, password, url, database)

    # 设置sqlalchemy不自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = False

    # 禁止自动提交数据处理
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False


