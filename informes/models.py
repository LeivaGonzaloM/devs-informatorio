from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Informe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()   # <--- CKEDITOR (Remplazado el 4 por ultima versión)!
    created = models.DateTimeField(auto_now_add=True)
    # image = models.ImageField(upload_to='posts/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    last_edited = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='edited_informes',
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.title} - Creado por {self.user.username}"


class CommentInforme(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Informe, on_delete=models.CASCADE, related_name='comments')
    
    # Comentario con CKEditor también
    content = models.TextField()

    dateCreated = models.DateTimeField(auto_now_add=True)
    gif_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Comentario de {self.user.username} en → {self.post.title}"