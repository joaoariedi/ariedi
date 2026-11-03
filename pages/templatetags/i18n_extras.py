from django import template
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def switch_lang_url(context, lang_code):
    """The current page's URL in another language, e.g. "/research" -> "/pt-br/research".

    Usage: ``<a href="{% switch_lang_url 'pt-br' %}">PT</a>``. Falls back to the current
    path when it cannot be resolved (e.g. a 404), which keeps the switcher harmless.
    """
    request = context["request"]
    return translate_url(request.path, lang_code)
