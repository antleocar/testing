__author__ = 'Antonio-PC'

from django import template
from django.core.urlresolvers import reverse
from django.templatetags.static import static
from django.core.files.storage import default_storage

register = template.Library()


@register.simple_tag
def navactive(request, urls):
    if request.path in (reverse(url) for url in urls.split() ):
        return "active"
    return ""


@register.simple_tag
def avatar(avatar):
    if avatar:
        if default_storage.exists(avatar.name):
            return avatar.url
        else:
            return static("webapp/image/logo_mini.png")
    else:
        return static("webapp/image/logo_mini.png")
