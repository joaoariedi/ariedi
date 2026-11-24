from django.urls import path, re_path

from .profiles import PROFILES
from .views import Home, Presentations, Research, SendMessage, serve_deck, serve_presentation

urlpatterns = [
    path("", Home.as_view(), name='home'),
    path("presentations", Presentations.as_view(), name='presentations'),
    path("research", Research.as_view(), name='research'),
    path("presentations/pdf/<str:filename>", serve_presentation, name='serve_presentation'),
    path("presentations/<slug:slug>", serve_deck, name='presentation_deck'),
    path("sendmessage", SendMessage.as_view(), name='sendmessage'),
    # the home page read for one need: /engineering, /security, /advisory, /ai-agents
    re_path(r"^(?P<profile>%s)$" % "|".join(PROFILES), Home.as_view(), name='profile'),
]
