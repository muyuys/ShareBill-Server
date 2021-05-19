# -*- coding: utf-8 -*-
# @Author : 13706
# @File : Report.py
# @Project: ShareBill
# @CreateTime : 2021/5/16 0:39:45
from .. import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = "Report"
    __table_args__ = {
        "mysql_charset": "utf8mb4"
    }
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    # 可以创建外键
    informer = db.Column(db.Integer)
    order_id = db.Column(db.String(30))
    reason = db.Column(db.String(100))
    introduction = db.Column(db.Text)
    pictures = db.Column(db.Text)
    createdAt = db.Column(db.DateTime)

    def __init__(self, informer, order_id, reason, introduction):
        self.informer = informer
        self.order_id = order_id
        self.reason = reason
        self.introduction = introduction
        self.createdAt = datetime.now()
