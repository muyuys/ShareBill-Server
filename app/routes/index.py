# -*- coding: utf-8 -*-
# @Author : 13706
# @File : index.py
# @Project: ShareBill
# @CreateTime : 2021/5/8 14:24:29
# 主要业务逻辑处理

import json
import re
import os
import uuid

from .. import db
from ..base import base
from flask import request, jsonify
from flask_sqlalchemy import Pagination
from qiniu import Auth, put_data
from ..models import Order, School, User, Report
from datetime import datetime
from ..utils.DateEncoder import DateEncoder


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def upload_img2qiniu(image):
    file_name = random_filename(image.filename)
    # 需要填写你的 Access Key 和 Secret Key
    access_key = 'gfffKLDehPag9WR4us2l0BKMjOagWgO0Z-QvAIq5'
    secret_key = 'BK-cK3wIB9ceR8uHZCVE2IbJpGkrdYFLqiCInqJF'
    q = Auth(access_key, secret_key)
    key = file_name

    bucket_url = "https://www.sharebill.top/"
    bucket_name = "xiaopin-order"
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key)
    ret, info = put_data(token, key, data=image.read())
    if info.status_code == 200:
        img_url = bucket_url + ret.get('key')
        db.session.commit()

    return img_url


def filter_emoji(desstr, restr=''):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


# TODO getopenid,sendSubscribeMessage 接口 创建一个新的蓝图 wechat,目前暂用云函数


@base.route('/post', methods=['POST'])
def post():
    res = {}
    data = request.get_data()
    json_re = json.loads(data)
    order_id = json_re['order_id']
    type = json_re['type']
    title = json_re['title']
    content = json_re['content']
    description = json_re['description']
    url = filter_emoji(json_re['url'])
    deadline = json_re['deadline']
    openid = json_re['openid']
    number = int(json_re['number'])
    # 获取对应的用户
    user = User.query.filter(User.openid == openid).first()
    order = Order(order_id, type, title, content, description, url, deadline, user.id, number - 1)
    user.participated_orders.append(order)
    order.add()
    res["res"] = "ok"
    return jsonify(res)


@base.route('/upload_order_img', methods=['POST'])
def upload_order_img():
    order_id = request.form.get('order_id', None)
    # 查找订单
    order = Order.query.filter_by(order_id=order_id).first()
    # 上传图片到七牛云,构建链接字符串
    image = request.files['image']
    image_url = upload_img2qiniu(image)
    if order.pictures is None:
        order.pictures = image_url + ";"
    else:
        order.pictures += image_url + ";"
    order.updatedAt = datetime.now()
    db.session.commit()
    res = {
        "old": order.pictures,
    }
    return jsonify(res)


@base.route('/get_order', methods=['POST', 'GET'])
def get_order():
    res = {'order_list': []}

    order_type = request.values.get('type')
    page = int(request.values.get('page'))
    # 对数据进行分页
    pagination = Order.query.filter(Order.status == "进行中", Order.type == order_type). \
        order_by(Order.createdAt.desc()).paginate(page, per_page=10, error_out=False)
    # 记录是否有下一页
    res['has_next'] = pagination.has_next
    res['all'] = pagination.total
    order_list = pagination.items
    # 已经使用事件 设置定时器来检查订单中是否有正在进行中的订单过期

    if order_list is not None:
        for order in order_list:
            # TODO 判断是否是该学校的订单
            res['order_list'].append(order.basic_view())
            # 获取发布人的学校
            res['order_list'][len(res['order_list']) - 1]['school'] = order.issuer.school
    db.session.commit()
    if len(res['order_list']) != 0:
        for order in res['order_list']:
            order['pictures'] = order['pictures'].split(';')
            # 删除分割后的最后一个空字符串
            del (order['pictures'][len(order['pictures']) - 1])
    # 如果直接使用jsonify datetime会被转换为世界标准时间的格式
    return json.dumps(res, cls=DateEncoder)


@base.route('/get_order_detail', methods=['POST', 'GET'])
def get_order_detail():
    res = {'order_detail': {}}
    order_id = request.values.get('order_id')
    openid = request.values.get('openid')
    user = User.query.filter(User.openid == openid).first()
    if user is None:
        is_collected = False
    else:
        sql = "select * from collection where order_id=\'%s\' and user_id=%d" % (order_id, user.id)
        collect_res = db.session.execute(sql).fetchall()
        is_collected = True if len(collect_res) > 0 else False
    order = Order.query.filter(Order.order_id == order_id).first()
    if order is not None:
        res['order_detail'] = order.to_dict()
        res['order_detail']['pictures'] = res['order_detail']['pictures'].split(';')
        # 删除分割后的最后一个空字符串
        del (res['order_detail']['pictures'][len(res['order_detail']['pictures']) - 1])
        # 获取发布人的学校
        # 如果用户没有进行认证,那么就为空
        # TODO 用户没有nickname和school
        res['order_detail']['school'] = order.issuer.school
        res['order_detail']['is_collect'] = is_collected

    return json.dumps(res, cls=DateEncoder)


@base.route('/my/orders/all', methods=['POST', 'GET'])
def get_my_all_orders():
    res = {'order_list': []}
    openid = request.values.get('openid')  # 用户的openid
    user = User.query.filter(User.openid == openid).first()

    if user is not None:
        order_list = user.participated_orders.all()
        for order in order_list:
            res['order_list'].append(order.basic_view())

    return json.dumps(res, cls=DateEncoder)


@base.route('/my/orders/status', methods=['POST', 'GET'])
def get_my_status_orders():
    res = {'order_list': []}
    status = request.values.get('status')  # 订单的状态
    openid = request.values.get('openid')  # 用户的openid
    user = User.query.filter(User.openid == openid).first()
    if user is not None:
        order_list = user.participated_orders.all()
        for order in order_list:
            if order.status == status:
                res['order_list'].append(order.basic_view())
    return json.dumps(res, cls=DateEncoder)


@base.route('/my/orders/collect', methods=['POST', 'GET'])
def get_my_collect():
    res = {'order_list': []}
    openid = request.values.get('openid')  # 用户的openid
    user = User.query.filter(User.openid == openid).first()
    if user is not None:
        order_list = user.collected_orders.all()
        for order in order_list:
            res['order_list'].append(order.basic_view())
    return json.dumps(res, cls=DateEncoder)


# 用户发起拼单,数据库将订单记录到user.participated_orders
@base.route('/participate', methods=['POST', 'GET'])
def participate():
    res = {}
    openid = request.values.get('openid')
    order_id = request.values.get('order_id')
    user = User.query.filter(User.openid == openid).first()
    order = Order.query.filter(Order.order_id == order_id).first()
    # 判断用户是否已经参与过该订单
    sql = "select * from participation where user_id=%d and order_id=\'%s\'" % (user.id, order_id)
    is_participated = db.session.execute(sql).fetchall()
    # 未参与
    if len(is_participated) == 0:
        order.number = order.number - 1
        if order.number == 0:
            order.status = "完成的"
        user.participated_orders.append(order)
        try:
            db.session.commit()
            res['result'] = True
        except Exception as e:
            print(e)
            res['result'] = False
            res['errMsg'] = "服务器出了点问题"
            return json.dumps(res)
    else:
        res['result'] = False
        res['errMsg'] = "你已参与过该拼单活动了"
    return json.dumps(res)


@base.route('/set_collect', methods=['POST', 'GET'])
def set_collect():
    res = {}
    openid = request.values.get('openid')
    order_id = request.values.get('order_id')
    is_collect = request.values.get('is_collect')
    user = User.query.filter(User.openid == openid).first()
    order = Order.query.filter(Order.order_id == order_id).first()
    # 用户之前未收藏，现在收藏，插入该订单
    if is_collect == "true":
        user.collected_orders.append(order)
    else:
        user.collected_orders.remove(order)
    try:
        db.session.commit()
        res['result'] = True
    except Exception as e:
        print(e)
        res['result'] = False
        return json.dumps(res)
    return json.dumps(res)


@base.route('/get_user_info', methods=['POST', 'GET'])
def get_user_info():
    res = {}
    openid = request.values.get('openid')
    user = User.query.filter(User.openid == openid).first()
    if user is None:
        res['result'] = False
    else:
        res['result'] = True
        res['school'] = user.school
        res['contact'] = user.contact
    return json.dumps(res)


@base.route('/get_issuer', methods=['POST', 'GET'])
def get_issuer():
    res = {}
    order_id = request.values.get("order_id")
    order = Order.query.filter(Order.order_id == order_id).first()
    res['issuer_openid'] = order.issuer.openid

    return json.dumps(res)


@base.route('/report', methods=['POST', 'GET'])
def report():
    openid = request.values.get('openid')
    order_id = request.values.get('order_id')
    reason = request.values.get('reason')
    introduction = request.values.get('introduction')
    user = User.query.filter(User.openid == openid).first()
    informer = user.id
    report = Report(informer, order_id, reason, introduction)

    try:
        db.session.add(report)
        db.session.commit()
    except Exception as e:
        print(e)
        return json.dumps({'result': False})
    return json.dumps({'result': True, 'report_id': report.id})


@base.route('/upload_report_img', methods=['POST'])
def upload_report_img():
    report_id = request.form.get('report_id', None)
    # 查找订单
    report = Report.query.filter_by(id=report_id).first()
    # 上传图片到七牛云,构建链接字符串
    if report is None:
        return json.dumps({'result': False})
    image = request.files['image']
    image_url = upload_img2qiniu(image)
    if report.pictures is None:
        report.pictures = image_url + ";"
    else:
        report.pictures += image_url + ";"
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        return json.dumps({'result': False})
    return json.dumps({'result': True})
