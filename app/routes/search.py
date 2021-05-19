# -*- coding: utf-8 -*-
# @Author : 13706
# @File : search.py
# @Project: ShareBill
# @CreateTime : 2021/5/12 23:35:25

import json

import os
import uuid

from .. import db
from ..base import base
from flask import request, jsonify
from ..models.Order import Order
from ..models.School import School
from ..utils.DateEncoder import DateEncoder


@base.route('/search/school', methods=['POST', 'GET'])
def search_school():
    """
    Gets: schoolName: 用于模糊搜索的校园名称

    Returns: schools: 搜索结果,包含学校名字、学校所在省份、市区
            result: 本次查询的结果,正常查询为true,服务器端错误为false

    """
    # TODO 将result改为code,判断是正常,服务端出错,客户端传递数据出错等
    res = {'schools': [], 'result': False}
    school_name = request.values.get('schoolName')
    schools = School.query.filter(School.school_name.like("%{name}%".format(name=school_name))).all()
    if schools is not None:
        for school in schools:
            res['schools'].append(school.school_view())
        res['result'] = True
    return json.dumps(res)



@base.route('/search/order', methods=['POST', 'GET'])
def search_order():
    res = {'orders': [], 'result': False}
    key = request.values.get('query')
    print(key)
    orders = Order.query.filter(Order.title.like("%{key}%".format(key=key))).all()
    print(orders)
    if orders is not None:
        for order in orders:
            res['orders'].append(order.basic_view())
        res['result'] = True
    return json.dumps(res, cls=DateEncoder)
