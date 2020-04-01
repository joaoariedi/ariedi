from django.urls import path

from .views import Home, SendMessage

urlpatterns = [
    path("", Home.as_view(), name='home'),
    path("sendmessage", SendMessage.as_view(), name='sendmessage'),
]
