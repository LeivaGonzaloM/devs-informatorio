from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class MensajeContacto(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    titulo = models.CharField(max_length=150)
    email = models.EmailField()
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo