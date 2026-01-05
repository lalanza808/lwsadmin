from random import choice
from datetime import datetime

from peewee import *
from monero.wordlists import English


db = SqliteDatabase("data/lws.db")


def get_random_words():
    e = English().word_list
    return f"{choice(e)}-{choice(e)}-{choice(e)}"


class User(Model):
    username = CharField()
    password = CharField()
    address = CharField()
    view_key = CharField()
    date = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db


class Wallet(Model):
    date = DateTimeField(default=datetime.utcnow)
    address = CharField()
    label = CharField(default=get_random_words, null=False)

    class Meta:
        database = db


db.create_tables([User, Wallet])
