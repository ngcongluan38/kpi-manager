from django import template
from django.conf import settings
from more_itertools import chunked
register = template.Library()


@register.filter()
def mul(a, b):
    return a*b


@register.filter()
def len_tag(a):
    return len(a)


@register.filter()
def chunk_data(l, n):
    return list(chunked(l, n))
