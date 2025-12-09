#posts/forms.py
from django.forms import ModelForm
from .models import Post

from django import forms
from .models import Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'image']


class CommentForm(forms.ModelForm):
    gif_url = forms.URLField(max_length=500, required=False)

    class Meta:
        model = Comment
        fields = ['content', 'gif_url'] 
        
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'input-field',
                'rows': 3,
                'placeholder': 'Deja tu comentario...'
            })
        }
