from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    try:
        return lst[int(index)]
    except (IndexError, ValueError, TypeError):
        return index