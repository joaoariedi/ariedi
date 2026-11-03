from django.urls import path

from .views import Home, Presentations, Research, SendMessage, serve_presentation

urlpatterns = [
    path("", Home.as_view(), name='home'),
    path("presentations", Presentations.as_view(), name='presentations'),
    path("research", Research.as_view(), name='research'),
    path("presentations/pdf/<str:filename>", serve_presentation, name='serve_presentation'),
    path("sendmessage", SendMessage.as_view(), name='sendmessage'),
]
