# -*- coding: utf-8 -*-
# @Author : 13706
# @File : __init__.py.py
# @Project: ShareBill
# @CreateTime : 2021/5/9 15:29:04

from flask import Blueprint

#base = Blueprint('base', __name__, url_prefix='/base')
base = Blueprint('base', __name__)
from ..routes import *