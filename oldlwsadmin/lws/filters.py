from monero.numbers import from_atomic
from quart import Blueprint

from lws.models import Wallet, get_random_words


bp = Blueprint('filters', 'filters')


@bp.app_template_filter('atomic')
def atomic(amt):
    return float(from_atomic(amt))


@bp.app_template_filter('shorten')
def shorten(s):
    return f"{s[:6]}...{s[-6:]}"

@bp.app_template_filter('find_label')
def find_label(s):
    w = Wallet.select().where(Wallet.address == s).first()
    if w:
        return w.label
    else:
        return get_random_words()