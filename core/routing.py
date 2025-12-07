from django.urls import re_path
from messagesapp.consumers import ChatConsumer
from django.urls import path
from channels.routing import URLRouter
from messagesapp.routing import websocket_urlpatterns
from . import consumers


websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<username>\w+)/$", ChatConsumer.as_asgi()),
]
