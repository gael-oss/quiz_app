# quiz/templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Récupère dictionary[key] ou '' si inexistant."""
    try:
        return dictionary.get(key, '')
    except Exception:
        return ''
