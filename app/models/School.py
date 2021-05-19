# -*- coding: utf-8 -*-
# @Author : 13706
# @File : School.py
# @Project: ShareBill
# @CreateTime : 2021/5/12 14:50:05
import json

from .. import db


class School(db.Model):
    __tablename__ = "School"
    __table_args__ = {
        "mysql_charset": "utf8mb4"
    }
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    school_id = db.Column(db.String(20))
    school_name = db.Column(db.String(255))
    province_id = db.Column(db.String(20))
    province_name = db.Column(db.String(255))
    city_id = db.Column(db.String(20))
    city_name = db.Column(db.String(255))
    level = db.Column(db.String(255))
    department = db.Column(db.String(255))
    other = db.Column(db.String(255))

    def school_view(self):
        view = {
            "id": self.id,
            "school_name": self.school_name,
            "provice_name": self.province_name,
            "city_name": self.city_name
        }
        return view
