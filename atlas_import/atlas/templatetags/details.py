import datetime
from django import template

register = template.Library()


@register.filter
def simple(value):
    if value is None or value == "":
        return ""

    if value is True:
        return "Ja"

    if value is False:
        return "Nee"

    if isinstance(value, datetime.date):
        return value.strftime("%d-%m-%Y")

    return value


@register.filter
def choice(value, field):
    v = getattr(value, field)

    if v is None or v == "":
        return ""

    display = getattr(value, 'get_{}_display'.format(field))()
    return "{} ({})".format(display, v)