from __future__ import absolute_import
from django import template
from django.db.models import get_model
from configuration.models import Configuration


register = template.Library()


@register.assignment_tag()
def get_configuration(config_string):
    split = config_string.rsplit('.', 1)
    if len(split) != 2:
        raise ValueError("%s is not a model" % config_string)

    config_class = get_model(*split)
    if config_class is None:
        raise ValueError("Could not find model " + config_string)

    if not issubclass(config_class, Configuration):
        raise ValueError("%s is not a Configuration" % config_string)

    return config_class.objects.get()
