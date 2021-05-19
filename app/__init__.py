# -*- coding: utf-8 -*-
# @Author : 13706
# @File : __init__.py.py
# @Project: ShareBill
# @CreateTime : 2021/5/9 18:34:26
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    from .base import base as base_blueprint
    app.register_blueprint(base_blueprint)
    return app
