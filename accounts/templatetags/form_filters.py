from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    attrs = field.field.widget.attrs.copy()
    attrs["class"] = css_class
    return field.as_widget(attrs=attrs)
