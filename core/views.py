from django.shortcuts import render, get_object_or_404
from posts.models import Post
from posts.forms import PostForm
from users.models import Profile
from messagesapp.models import Message

# Fatcs inicio 
def home(request):
    posts = Post.objects.all()
    unread = 0
    if request.user.is_authenticated:
        unread = request.user.received_messages.filter(is_read=False).count()

    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)

    return render(request, 'index.html', {
         "unread": unread,
        'profile': profile,
        'posts': posts,
    })

def nosotros(request):
      return render(request, 'nosotros/nosotros.html')

def postDetail(request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(instance=post)
        return render(request, 'index.html', {'post': post, 'form': form})

def contacto(request):
      return render(request, 'contacto/contacto.html')