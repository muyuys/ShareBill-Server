from .. import db

participation = db.Table('participation',
                         db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
                         db.Column('order_id', db.String(30), db.ForeignKey('Order.order_id')))

collection = db.Table('collection',
                      db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
                      db.Column('order_id', db.String(30), db.ForeignKey('Order.order_id')))


class User(db.Model):
    __tablename__ = "User"
    __table_args__ = {
        "mysql_charset": "utf8mb4"
    }
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    openid = db.Column(db.String(40))  # 使用微信小程序的openid
    nickname = db.Column(db.String(40))
    contact = db.Column(db.String(255), nullable=False)  # 用户的联系方式,不限于手机号
    school = db.Column(db.String(255))
    # 所有我发布的订单(无论是什么状态)，一对多关系，order.issuer_id 对应用户id
    posted_order = db.relationship('Order', backref='issuer', lazy='dynamic')
    # 我参与的订单,包括完成、进行中、过期的的订单,多对多关系，查询后根据状态
    participated_orders = db.relationship('Order', secondary=participation,
                                          backref=db.backref('participator', lazy='dynamic'),
                                          lazy='dynamic')
    # 我收藏的订单,多对多关系,有多个订单收藏,每个订单也会被多个用户收藏
    collected_orders = db.relationship('Order', secondary=collection,
                                       backref=db.backref('collector', lazy='dynamic'),
                                       lazy='dynamic')

    def __init__(self, openid, contact, school):
        self.openid = openid
        self.contact = contact
        self.school = school

    def add(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(e)
            return e

    def update(self):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return e

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
