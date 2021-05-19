import random

from .. import db
from datetime import datetime


def order_code():
    code = datetime.now().strftime('%Y%m%d%H%M%S')
    for i in range(6):
        t = random.randrange(0, 9)
        code += str(t)
    return code


class Order(db.Model):
    __tablename__ = "Order"
    __table_args__ = {
        "mysql_charset": "utf8mb4"
    }

    # TODO 数据分页
    order_id = db.Column(db.String(30), primary_key=True)
    type = db.Column(db.Enum('外卖', '购物', '拼车', '合租'), default='购物', nullable=False)
    title = db.Column(db.String(100))
    content = db.Column(db.String(100))
    description = db.Column(db.String(200))
    url = db.Column(db.String(300))
    deadline = db.Column(db.DateTime)
    issuer_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    number = db.Column(db.Integer, default=2)
    status = db.Column(db.Enum('进行中', '完成的', '过期的'), default='进行中')
    pictures = db.Column(db.Text)  # 图片地址数组，使用字符串保存，以分号分隔
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)

    def __init__(self, order_id, type, title, content, description, url, deadline, issuer_id, number):
        self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        self.pictures = ""
        self.order_id = order_id
        self.type = type
        self.title = title
        self.content = content
        self.description = description
        self.url = url
        self.deadline = deadline
        self.issuer_id = issuer_id
        self.number = number

    def add(self):
        # 添加时,向"participation"表添加(order_id,issuer_id)
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return e

    def __repr__(self):
        return '<Title: %r order_id: %r>' % (self.title, self.order_id)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def basic_view(self):
        return {
            "order_id": self.order_id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "deadline": self.deadline,
            "status": self.status,
            "pictures": self.pictures
        }
