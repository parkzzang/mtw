from django import template

register = template.Library()

@register.filter
def get_item(form, field_name):
    return form[field_name]
