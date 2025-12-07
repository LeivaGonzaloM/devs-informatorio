from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"


# Función útil para obtener la conversación entre 2 usuarios
def get_chat_messages(user1, user2):
    return Message.objects.filter(
        models.Q(sender=user1, receiver=user2) |
        models.Q(sender=user2, receiver=user1)
    ).order_by("timestamp")
