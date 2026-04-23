from django import template

register = template.Library()

@register.filter
def get_dynamic_attr(obj, attr_name):
    """
    Usage in template:
    {{ object|get_dynamic_attr:"field_name" }}
    """
    return getattr(obj, attr_name, None)
