# -*- coding: utf-8 -*-
# @Author : 13706
# @File : DateEncoder.py
# @Project: ShareBill
# @CreateTime : 2021/5/12 14:25:15
import datetime
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)
