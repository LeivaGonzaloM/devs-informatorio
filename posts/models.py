#posts/models.py
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/' , verbose_name="Imagen: " ,null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Campos para el Update de los posts:
    last_edited = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        related_name='edited_posts',
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title + ' - Creado por:' + self.user.username

    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1500)
    dateCreated = models.DateTimeField(auto_now_add=True)

    gif_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Comentario de {self.user} en -> {self.post}"
    