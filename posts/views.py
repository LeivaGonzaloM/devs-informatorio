#posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post, Comment
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Create your views here.

# def posts(request):
#     posts = Post.objects.all()
#     return render(request, 'posts.html', {
#         'posts': posts
#     })

def posts(request):

    if request.user.is_authenticated and request.user.is_superuser:
        post_list = Post.objects.all().order_by('-id')  # Admin ve todo
    else:
        post_list = Post.objects.filter(oculto=False).order_by('-id')  

    PAGINATION_LIMIT = 8  
    paginator = Paginator(post_list, PAGINATION_LIMIT)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts.html', {
        'page_obj': page_obj
    })


def postDetail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().order_by('-dateCreated')

    # 🔒 1. Comprobación de visibilidad
    # Si el post está oculto y NO es admin → bloquear acceso
    if post.oculto and not (request.user.is_authenticated and request.user.is_superuser):
        return render(request, "posts/post_oculto.html", {"post": post})

    # 💬 2. Manejo de comentarios
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('signin')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('detallePost', post_id=post.id)
    else:
        form = CommentForm()

    # 📦 3. Render normal para posts visibles o admin
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }

    return render(request, 'posts/postDetail.html', context)

# Editar/eliminar comentarios en el lugar START
@login_required
@require_POST
def editarCommentAJAX(request, id):
    comment = get_object_or_404(Comment, id=id)
    if request.user != comment.user and not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permiso'}, status=403)

    content = request.POST.get('content', '').strip()
    if content:
        comment.content = content
        comment.save()
        return JsonResponse({'success': True, 'content': comment.content})
    return JsonResponse({'error': 'El contenido no puede estar vacío'}, status=400)

@login_required
@require_POST
def eliminarCommentAJAX(request, id):
    comment = get_object_or_404(Comment, id=id)
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'No tienes permiso'}, status=403)

# Editar/eliminar comentarios en el lugar END
@login_required
def createPost(request):
    if request.method == 'GET':
        return render(request, 'crud/createPost.html', {
        'form' : PostForm
        })
    else:
        try:
            form = PostForm(request.POST, request.FILES)
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return redirect('posts')
        except ValueError:
            return render(request, 'crud/createPost.html', {
            'form' : PostForm,
            'error' : 'Por favor verifique los datos.'
        })

@login_required
def editPost(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            edited_post = form.save(commit=False)

            # ❗ Mantener el usuario ORIGINAL del post
            # edited_post.user = request.user   ❌ NO HACER ESTO

            # 🔥 Registrar edición:
            edited_post.edited_by = request.user
            edited_post.last_edited = timezone.now()

            edited_post.save()

            return redirect('detallePost', post.id)

        return render(request, 'crud/editPost.html', {
            'formulario': form,
            'error': 'Por favor verifica los datos.'
        })

    else:
        formulario = PostForm(instance=post)
        return render(request, 'crud/editPost.html', {
            'formulario': formulario
        })



@login_required
def deletePost(request, post_id):
      post = get_object_or_404(Post, pk=post_id)

      # Si es el dueño o es admin → puede borrar
      if request.user == post.user or request.user.is_staff or request.user.is_superuser:
            if request.method == 'GET':
                post.delete()
                return redirect('posts')
