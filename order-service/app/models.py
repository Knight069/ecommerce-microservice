# application/models.py
from . import db
from datetime import datetime
import logging


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    items = db.relationship('OrderItem', backref='orderItem')
    is_open = db.Column(db.Boolean, default=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __init__(self):
        self.log = logging.getLogger("order-service")

    def create(self, user_id):
        """
        This method creates order for the user
        :param user_id:
        :return:
        """
        try:
            self.log.info("creating order for user id {}".format(user_id))
            self.user_id = user_id
            self.is_open = True
        except Exception as e:
            self.log.error(e)
            raise e
        return self

    def to_json(self):
        try:
            self.log.info("converting items into json")
            items = []
            for i in self.items:
                items.append(i.to_json())
        except Exception as e:
            self.log.error(e)
            raise e
        return {
            'items': items,
            'is_open': self.is_open,
            'user_id': self.user_id
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity
        self.log = logging.getLogger("order-service")

    def to_json(self):
        try:
            self.log.info(f"product-service: {self.product_id}, 'quantity': {self.quantity}")
            return {
                'product-service': self.product_id,
                'quantity': self.quantity
            }
        except Exception as e:
            self.log.error(e)
            raise e