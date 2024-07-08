# custom_filters.py

from django import template

register = template.Library()

@register.filter
def is_instance(value, class_str):
    try:
        return isinstance(value, eval(class_str))
    except (NameError, TypeError):
        return False
