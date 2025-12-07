#posts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post, Comment
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
    # 1. Obtener todos los posts, ordenados por fecha de creación (los más nuevos primero)
    post_list = Post.objects.all().order_by('-id') # Ordeno por ID descendente

    # 2. Configurar el Paginator: 8 posts por página (4 columnas x 2 filas)
    PAGINATION_LIMIT = 8 # Define cuántos posts quieres por página
    paginator = Paginator(post_list, PAGINATION_LIMIT) 

    # 3. Obtener el número de página de la URL (ej: /articulos/?page=2)
    # Por defecto, si no hay 'page' en la URL, es la página 1.
    page_number = request.GET.get('page')
    
    # 4. Obtener el objeto de página
    page_obj = paginator.get_page(page_number)
    
    # 5. Pasar el objeto de página al contexto
    return render(request, 'posts.html', {
        # ¡IMPORTANTE! Ahora pasas page_obj, NO 'posts'
        'page_obj': page_obj 
    })

def postDetail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().order_by('-dateCreated')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('signin')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('detallePost', post_id=post.id)  # ← FIX
    else:
        form = CommentForm()

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
    post = Post.objects.get(pk=post_id)

    if request.method == 'POST':
        # Formulario con el instance para editar
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.user = request.user  # opcional si querés mantener el usuario
            edited_post.save()
            return redirect('detallePost', post.id)  # Redirige al detalle del post  # redirigir a donde quieras
        else:
            # Si el formulario no es válido, mostrar errores
            return render(request, 'crud/editPost.html', {
                'formulario': form,
                'error': 'Por favor verifica los datos.'
            })
    else:
        # GET: mostrar formulario prellenado
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
