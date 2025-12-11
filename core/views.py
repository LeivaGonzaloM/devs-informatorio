from django.shortcuts import render, get_object_or_404
from posts.models import Post
from posts.forms import PostForm
from users.models import Profile
from django.core.paginator import Paginator

# Fatcs inicio 
def home(request):
    # Filtrado según el usuario
    if request.user.is_authenticated and request.user.is_superuser:
        posts_list = Post.objects.all().order_by('-id')  # Admin ve todo
    else:
        posts_list = Post.objects.filter(oculto=False).order_by('-id')  # Usuarios normales solo visibles

    # Opcional: paginación
    PAGINATION_LIMIT = 8
    paginator = Paginator(posts_list, PAGINATION_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Perfil del usuario autenticado
    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)

    return render(request, 'index.html', {
        'profile': profile,
        'page_obj': page_obj,  # usar en template en vez de 'posts'
        'es_admin': request.user.is_superuser,
    })

def nosotros(request):
      return render(request, 'nosotros/nosotros.html')

# def postDetail(request, post_id):
#         post = get_object_or_404(Post, pk=post_id)
#         form = PostForm(instance=post)
#         return render(request, 'index.html', {'post': post, 'form': form})

def contacto(request):
      return render(request, 'contacto/contacto.html')