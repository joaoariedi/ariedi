from django.urls import path

from .views import Home, contact, SendMessage

urlpatterns = [
    path("", Home.as_view(), name='home'),
    path("contact", contact, name='contact'),
    path("sendmessage", SendMessage.as_view(), name='sendmessage'),
]
