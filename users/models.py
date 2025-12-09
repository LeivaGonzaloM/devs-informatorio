from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now

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
    # --- NUEVO MÉTODO SEGURO PARA AVATAR ---
    def avatar_url(self):
        """
        Devuelve una URL válida para el avatar, incluso si falta,
        el archivo no existe o está vacío.
        """
        try:
            if self.avatar and hasattr(self.avatar, "url"):
                return self.avatar.url
        except:
            pass

        return "/static/img/default-avatar.png"

class UserReport(models.Model):
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_user')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reporter')
    reason = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Reporte sobre {self.reported_user.username} por {self.reporter.username}"
    

# SISTEMA DE ADVERTENCIAS A USUARIOS

class Warning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warnings')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='warnings_given')

    mensaje = models.TextField()

    nivel = models.CharField(max_length=10, choices=[
        ("leve", "Leve"),
        ("media", "Media"),
        ("grave", "Grave"),
    ])

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    is_read = models.BooleanField(default=False)

    def check_active(self):
        """Actualiza el estado si ya expiró."""
        if self.expires_at and now() >= self.expires_at:
            self.active = False
            self.save()
        return self.active

    def is_active(self):
        """Solo devuelve si está activa sin modificar el modelo."""
        if self.expires_at is None:
            return True
        return now() < self.expires_at

    def remaining_time(self):
        """Devuelve texto útil: '2 días, 3 horas' o None."""
        if not self.expires_at:
            return None  # advertencia permanente

        delta = self.expires_at - now()
        if delta.total_seconds() <= 0:
            return None

        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        partes = []
        if days > 0:
            partes.append(f"{days}d")
        if hours > 0:
            partes.append(f"{hours}h")
        if minutes > 0:
            partes.append(f"{minutes}m")

        return " ".join(partes)

    def __str__(self):
        return f"Advertencia para {self.user.username}"

    