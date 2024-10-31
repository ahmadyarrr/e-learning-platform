from django.template import Library

register = Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except:
        return None

@register.filter
def get_key_vale(dic, key):
    if key in dic:
        return dic[key] * 100
    else:
        return 0 