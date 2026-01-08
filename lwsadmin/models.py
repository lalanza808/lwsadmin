from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.inspection import inspect

from lwsadmin.factory import db


def rand_id():
    return uuid4().hex


class User(db.Model):
    id = db.Column(db.String(80), primary_key=True, default=rand_id)
    create_date = db.Column(db.DateTime, server_default=func.now())
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(60), unique=True)
    address = db.Column(db.String(150), unique=True)
    view_key = db.Column(db.String(150), unique=True)

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id

    def __repr__(self):
        return self.username

class Account(db.Model):
    id = db.Column(db.String(80), primary_key=True, default=rand_id)
    create_date = db.Column(db.DateTime, server_default=func.now())
    address = db.Column(db.String(150), unique=True)
    view_key = db.Column(db.String(150), unique=True)
    payment_account_id = db.Column(db.Integer, unique=False)
    payment_address_id = db.Column(db.Integer, unique=True)
    payment_address = db.Column(db.String(150), unique=True)
    start_height = db.Column(db.Integer, unique=False)
    active = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.address

class Payment(db.Model):
    tx_hash = db.Column(db.String(150), primary_key=True, unique=True)
    create_date = db.Column(db.DateTime, server_default=func.now())
    account_id = db.Column(db.String(80), db.ForeignKey('account.id'))
    amount = db.Column(db.BigInteger, unique=False)
    price_per_block = db.Column(db.BigInteger, unique=False)
    confirmed = db.Column(db.Boolean, unique=False, default=False)
    dropped = db.Column(db.Boolean, unique=False, default=False)

    def as_json(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def get_blocks_to_scan(self):
        return int(self.amount / self.price_per_block)
    


    def __repr__(self):
        return self.tx_hash
