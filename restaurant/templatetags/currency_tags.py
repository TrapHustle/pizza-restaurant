from django import template

register = template.Library()

@register.filter
def format_fcfa(value):
    try:
        return f"{float(value):,.2f} FCFA".replace(",", " ")
    except (ValueError, TypeError):
        return value