from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
import json

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.other_username = self.scope["url_route"]["kwargs"]["username"]

        users_sorted = sorted([self.user.username, self.other_username])
        self.room_name = f"chat_{users_sorted[0]}_{users_sorted[1]}"

        # Unirse al grupo
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        # Enviar historial
        messages = await self.get_messages()
        for msg in messages:
            await self.send(text_data=json.dumps({
                "sender": msg.sender.username,
                "message": msg.content,
                "time": msg.timestamp.strftime("%H:%M")
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("message", "").strip()
        if not content:
            return

        other_user = await self.get_user(self.other_username)
        msg = await self.save_message(self.user, other_user, content)

        # Enviar mensaje a todos los miembros del grupo
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "sender": self.user.username,
                "message": msg.content,
                "time": msg.timestamp.strftime("%H:%M")
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # Métodos DB
    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return Message.objects.create(sender=sender, receiver=receiver, content=content)

    @database_sync_to_async
    def get_messages(self):
        other_user = User.objects.get(username=self.other_username)
        return Message.objects.filter(
            sender=self.user, receiver=other_user
        ) | Message.objects.filter(
            sender=other_user, receiver=self.user
        ).order_by("timestamp")


