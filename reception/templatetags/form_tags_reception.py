from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter(name='add_placeholder')
def add_placeholder(field, text):
    return field.as_widget(attrs={"placeholder": text})

@register.filter(name='add_attrs')
def add_attrs(field, args):
    attrs = {}
    for arg in args.split(','):
        k, v = arg.split('=')
        attrs[k.strip()] = v.strip()
    return field.as_widget(attrs=attrs)