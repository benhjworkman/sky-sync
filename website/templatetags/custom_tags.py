from django import template
import math
from django.shortcuts import get_object_or_404
from ..models import Location

register = template.Library()
@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    if user is None:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name='calculate_distance')
def calcDistance(x1, x2, y1, y2):
    x1 = x1 * (math.pi / 180)
    x2 = x2 * (math.pi / 180)
    y1 = y1 * (math.pi / 180)
    y2 = y2 * (math.pi / 180)
    earth_radius = 6371
    dlat = x2 - x1
    dlong = y2 - y1

    a = ((math.sin(dlat / 2) ** 2) + math.cos(x1)) * (math.cos(x2) * ((math.sin(dlong / 2)) ** 2))
    c = 2 * math.atan2((math.sqrt(a)), (math.sqrt(1 - a)))
    d = earth_radius * c
    return d

@register.filter(name="get_location_name")
def translate_location_name(location_id):
    location = get_object_or_404(Location, id=location_id)
    return location.location_name

