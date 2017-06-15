import datetime

from django import template
from django.contrib.gis import geos
from django.utils import safestring

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

    if isinstance(value, geos.Point):
        return "{:.0f}, {:.0f}".format(value.x, value.y)

    return value


@register.filter
def choice(value, field):
    v = getattr(value, field)

    if v is None or v == "":
        return ""

    display = getattr(value, 'get_{}_display'.format(field))()
    return "{} ({})".format(display, v)


@register.filter
def oppervlak(value):
    if value is None:
        return ""

    return safestring.mark_safe("{} m<sup>2</sup>".format(value))
