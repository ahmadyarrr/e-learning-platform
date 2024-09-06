from django.template import Library

register = Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except:
        return None
