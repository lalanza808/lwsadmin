from monero.numbers import from_atomic
from flask import Blueprint

bp = Blueprint('filters', 'filters')


@bp.app_template_filter('atomic')
def atomic(amt):
    return float(from_atomic(amt))


@bp.app_template_filter('shorten')
def shorten(s):
    return f"{s[:6]}...{s[-6:]}"
