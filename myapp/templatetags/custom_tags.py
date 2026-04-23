from django import template

register = template.Library()

@register.simple_tag
def range_list(start, end):
    """
    Usage in template:
    {% range_list 1 5 as range %}
    {% for i in range %}
        {{ i }}
    {% endfor %}
    """
    return range(start, end + 1)
