from django.urls import path
from .views import inbox, chat_view, send_message

urlpatterns = [
    path("mensajes/", inbox, name="inbox"),
    path("mensajes/<str:username>/", chat_view, name="chat"),
    path("send/<str:username>/", send_message, name="send_message"),
]
