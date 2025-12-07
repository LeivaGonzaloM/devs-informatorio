from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

def user_avatar_path(instance, filename):
    return f'profiles/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Nombre completo
    full_name = models.CharField(max_length=150, blank=True, null=True)

    # Avatar corregido
    avatar = models.ImageField(upload_to=user_avatar_path, default='profiles/default.png')

    # Otros datos
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    # Nuevo sistema de bloqueos
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)

    def block(self, minutes=None, hours=None, days=None):
        """Bloquea al usuario por el tiempo indicado."""
        self.is_blocked = True

        delta = timedelta(
            minutes=minutes or 0,
            hours=hours or 0,
            days=days or 0
        )

        self.blocked_until = timezone.now() + delta
        self.save()

    def unblock(self):
        """Desbloquea al usuario."""
        self.is_blocked = False
        self.blocked_until = None
        self.save()
    @property
    def is_currently_blocked(self):
        """Retorna True si sigue bloqueado"""
        if not self.is_blocked:
            return False
        
        if self.blocked_until and timezone.now() < self.blocked_until:
            return True
        
        # Si el tiempo ya expiró, desbloquear automáticamente
        self.unblock()
        return False

class UserReport(models.Model):
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_user')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reporter')
    reason = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Reporte sobre {self.reported_user.username} por {self.reporter.username}"