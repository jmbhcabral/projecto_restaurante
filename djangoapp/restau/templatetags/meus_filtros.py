from django import template
import os

register = template.Library()


@register.filter
def basename(value):
    return os.path.basename(value)


@register.filter
def get_item(dictionary, key):

    """ Obtém um item de um dicionário no template """
    return dictionary.get(key, "")