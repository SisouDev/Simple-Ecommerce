from atexit import register
from django.template import Library
from utils import utils

register = Library()

@register.filter
def formata_preco(val)->str:
    return utils.formata_preco(val)

@register.filter
def cart_total(carrinho):
    return utils.cart_total(carrinho)

@register.filter
def cart_totals(carrinho):
    return utils.cart_totals(carrinho)