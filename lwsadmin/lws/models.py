from random import choice
from datetime import datetime

from peewee import *
from monero.wordlists import English


db = SqliteDatabase("data/lws.db")


def get_random_words():
    e = English().word_list
    return f"{choice(e)}-{choice(e)}-{choice(e)}-{choice(e)}"


class Wallet(Model):
    email_address = CharField(null=False)
    public_address = CharField(null=False, unique=True)
    secret_view_key = CharField(null=False)
    label = CharField(default=get_random_words, null=False)
    date = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db


db.create_tables([Wallet])
