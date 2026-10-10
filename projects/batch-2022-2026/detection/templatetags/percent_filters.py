from django import template

register = template.Library()

@register.filter
def to_percent(value):
    try:
        return float(value) * 100
    except Exception:
        return value
