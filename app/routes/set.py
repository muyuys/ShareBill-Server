# -*- coding: utf-8 -*-
# @Author : 13706
# @File : set.py
# @Project: ShareBill
# @CreateTime : 2021/5/13 0:26:56
import json

import os
import uuid

from .. import db
from ..base import base
from flask import request, jsonify
from ..models.Order import Order
from ..models.User import User


@base.route('/set/user', methods=['POST', 'GET'])
def set_user():
    res = {}
    openid = request.values.get('openid')
    contact = request.values.get('contact')
    school = request.values.get('school')
    user = User.query.filter(User.openid == openid).first()
    # 已经存在就修改
    if user is not None:
        if contact is not None:
            user.contact = contact
        if school is not None:
            user.school = school
    # 不存在就创建
    else:
        user = User(openid, contact, school)
        db.session.add(user)
    db.session.commit()
    res['result'] = True
    return json.dumps(res)
